import { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

interface ArtworkViewer3DProps {
  imageUrl: string;
  width?: number;
  height?: number;
}

function Scene({ imageUrl }: { imageUrl: string }) {
  const textureRef = useRef<THREE.Texture | null>(null);

  useEffect(() => {
    const textureLoader = new THREE.TextureLoader();
    textureLoader.load(imageUrl, (texture) => {
      textureRef.current = texture;
    });
  }, [imageUrl]);

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <mesh>
        <planeGeometry args={[3, 2]} />
        <meshStandardMaterial map={textureRef.current || null} side={THREE.DoubleSide} />
      </mesh>
      <OrbitControls enableDamping dampingFactor={0.05} />
    </>
  );
}

const ArtworkViewer3D = ({ imageUrl, width = 800, height = 600 }: ArtworkViewer3DProps) => {
  return (
    <Box sx={{ width, height }}>
      <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
        <Scene imageUrl={imageUrl} />
      </Canvas>
    </Box>
  );
};

export default ArtworkViewer3D;
