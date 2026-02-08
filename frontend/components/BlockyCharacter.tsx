'use client'

import { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'

type Animation = 'wave' | 'point' | 'idle'

interface BlockyCharacterProps {
  animation: Animation
  position?: [number, number, number]
  scale?: number
  rotation?: [number, number, number]
}

export default function BlockyCharacter({
  animation,
  position = [0, 0, 0],
  scale = 1,
  rotation = [0, 0, 0],
}: BlockyCharacterProps) {
  const { scene } = useGLTF('/character-q.glb')

  const clonedScene = useMemo(() => {
    const clone = scene.clone(true)
    clone.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.material = child.material.clone()
        const map = child.material.map
        if (map) {
          map.magFilter = THREE.NearestFilter
          map.minFilter = THREE.NearestFilter
          map.needsUpdate = true
        }
      }
    })
    return clone
  }, [scene])

  const groupRef = useRef<THREE.Group>(null)

  // Find arm nodes
  const armRefs = useRef<{ left: THREE.Object3D | null; right: THREE.Object3D | null }>({
    left: null,
    right: null,
  })

  useEffect(() => {
    const nextRefs: { left: THREE.Object3D | null; right: THREE.Object3D | null } = {
      left: null,
      right: null,
    }
    clonedScene.traverse((child) => {
      if (child.name === 'arm-left') nextRefs.left = child
      if (child.name === 'arm-right') nextRefs.right = child
    })
    armRefs.current = nextRefs
  }, [clonedScene])

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    const { left, right } = armRefs.current

    switch (animation) {
      case 'wave':
        // Right arm waves up and down
        if (right) {
          right.rotation.x = -Math.PI * 1.0 + Math.sin(t * 3) * 0.3
          right.rotation.z = -0.5
        }
        // Left arm stays relaxed
        if (left) {
          left.rotation.x = Math.sin(t * 0.5) * 0.05
          left.rotation.z = 0
        }
        break

      case 'point':
        // Right arm points toward the phone (extended forward/inward), slight bob
        if (right) {
          right.rotation.x = -Math.PI * 0.45 + Math.sin(t * 1.5) * 0.05
          right.rotation.z = 0.3
        }
        if (left) {
          left.rotation.x = Math.sin(t * 0.8) * 0.05
          left.rotation.z = 0
        }
        break

      case 'idle':
        // Both arms gently sway
        if (right) {
          right.rotation.x = Math.sin(t * 0.8) * 0.15
          right.rotation.z = Math.sin(t * 0.6) * 0.05
        }
        if (left) {
          left.rotation.x = Math.sin(t * 0.8 + Math.PI) * 0.15
          left.rotation.z = -Math.sin(t * 0.6 + Math.PI) * 0.05
        }
        break
    }

    // Gentle body Y-rotation sway to show off 3D depth
    if (groupRef.current) {
      groupRef.current.rotation.y = rotation[1] + Math.sin(t * 0.4) * 0.15
    }
  })

  return (
    <group ref={groupRef} position={position} scale={scale} rotation={rotation}>
      <primitive object={clonedScene} />
    </group>
  )
}

useGLTF.preload('/character-q.glb')
