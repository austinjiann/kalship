'use client'

import { Canvas } from '@react-three/fiber'
import { Suspense } from 'react'
import BlockyCharacter from './BlockyCharacter'

interface CharacterPreviewProps {
  animation?: 'wave' | 'point' | 'idle'
  size?: { width: number; height: number }
  rotationY?: number
}

export default function CharacterPreview({
  animation = 'idle',
  size = { width: 400, height: 500 },
  rotationY = 0.3,
}: CharacterPreviewProps) {
  return (
    <div style={{ width: size.width, height: size.height }}>
      <Canvas camera={{ position: [1.5, 1.5, 5.5], fov: 45 }} dpr={[1, 1.5]}>
        <Suspense fallback={null}>
          <ambientLight intensity={0.6} />
          <directionalLight position={[5, 8, 5]} intensity={1} />
          <directionalLight position={[-3, 4, -2]} intensity={0.3} />
          <BlockyCharacter animation={animation} position={[0, -1.5, 0]} scale={1.2} rotation={[0, rotationY, 0]} />
        </Suspense>
      </Canvas>
    </div>
  )
}
