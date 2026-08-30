import { useRef, useEffect } from 'react';
import * as THREE from 'three';

const ATOM_COLORS: Record<string, number> = {
  C: 0x27272a,
  O: 0xdc2626,
  N: 0x2563eb,
  H: 0xd4d4d8,
  S: 0xca8a04,
  P: 0xea580c,
  Cl: 0x16a34a,
  F: 0x06b6d4,
};

interface AtomDef {
  pos: [number, number, number];
  element: string;
  radius: number;
}

interface BondDef {
  from: number;
  to: number;
}

const CAFFEINE_ATOMS: AtomDef[] = [
  { pos: [0, 0, 0], element: 'N', radius: 0.35 },
  { pos: [1.2, 0.7, 0.3], element: 'C', radius: 0.38 },
  { pos: [2.4, 0, -0.2], element: 'N', radius: 0.35 },
  { pos: [2.4, -1.4, 0.1], element: 'C', radius: 0.38 },
  { pos: [1.2, -2.1, 0.5], element: 'C', radius: 0.38 },
  { pos: [0, -1.4, 0.3], element: 'C', radius: 0.38 },
  { pos: [-1.3, -2.0, -0.1], element: 'O', radius: 0.32 },
  { pos: [1.2, 2.1, 0.1], element: 'O', radius: 0.32 },
  { pos: [3.6, 0.7, -0.5], element: 'C', radius: 0.38 },
  { pos: [3.6, -2.1, -0.3], element: 'N', radius: 0.35 },
  { pos: [4.5, -1.2, -0.6], element: 'C', radius: 0.38 },
  { pos: [-1.2, 0.7, -0.4], element: 'C', radius: 0.3 },
  { pos: [3.6, -3.5, 0.1], element: 'C', radius: 0.3 },
  { pos: [1.2, -3.4, 0.8], element: 'N', radius: 0.35 },
  { pos: [2.4, -3.9, 0.5], element: 'C', radius: 0.38 },
];

const CAFFEINE_BONDS: BondDef[] = [
  { from: 0, to: 1 }, { from: 1, to: 2 }, { from: 2, to: 3 },
  { from: 3, to: 4 }, { from: 4, to: 5 }, { from: 5, to: 0 },
  { from: 5, to: 6 }, { from: 1, to: 7 }, { from: 2, to: 8 },
  { from: 3, to: 9 }, { from: 9, to: 10 }, { from: 10, to: 8 },
  { from: 0, to: 11 }, { from: 9, to: 12 }, { from: 4, to: 13 },
  { from: 13, to: 14 }, { from: 14, to: 12 },
];

const BENZENE_ATOMS: AtomDef[] = [
  { pos: [0, 1.4, 0], element: 'C', radius: 0.28 },
  { pos: [1.21, 0.7, 0], element: 'C', radius: 0.28 },
  { pos: [1.21, -0.7, 0], element: 'C', radius: 0.28 },
  { pos: [0, -1.4, 0], element: 'C', radius: 0.28 },
  { pos: [-1.21, -0.7, 0], element: 'C', radius: 0.28 },
  { pos: [-1.21, 0.7, 0], element: 'C', radius: 0.28 },
  { pos: [0, 2.2, 0], element: 'H', radius: 0.18 },
  { pos: [1.9, 1.1, 0], element: 'H', radius: 0.18 },
  { pos: [1.9, -1.1, 0], element: 'H', radius: 0.18 },
  { pos: [0, -2.2, 0], element: 'H', radius: 0.18 },
  { pos: [-1.9, -1.1, 0], element: 'H', radius: 0.18 },
  { pos: [-1.9, 1.1, 0], element: 'H', radius: 0.18 },
];

const BENZENE_BONDS: BondDef[] = [
  { from: 0, to: 1 }, { from: 1, to: 2 }, { from: 2, to: 3 },
  { from: 3, to: 4 }, { from: 4, to: 5 }, { from: 5, to: 0 },
  { from: 0, to: 6 }, { from: 1, to: 7 }, { from: 2, to: 8 },
  { from: 3, to: 9 }, { from: 4, to: 10 }, { from: 5, to: 11 },
];

const WATER_ATOMS: AtomDef[] = [
  { pos: [0, 0, 0], element: 'O', radius: 0.3 },
  { pos: [0.75, 0.6, 0], element: 'H', radius: 0.2 },
  { pos: [-0.75, 0.6, 0], element: 'H', radius: 0.2 },
];
const WATER_BONDS: BondDef[] = [
  { from: 0, to: 1 }, { from: 0, to: 2 }
];

function buildMoleculeGroup(atoms: AtomDef[], bonds: BondDef[], cylinderRadius = 0.05) {
  const group = new THREE.Group();

  atoms.forEach((atom) => {
    const geometry = new THREE.SphereGeometry(atom.radius, 28, 28);
    const material = new THREE.MeshPhysicalMaterial({
      color: ATOM_COLORS[atom.element] || 0x71717a,
      roughness: 0.25,
      metalness: 0.15,
      clearcoat: 0.5,
      clearcoatRoughness: 0.2,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(...atom.pos);
    group.add(mesh);
  });

  bonds.forEach((bond) => {
    const startAtom = atoms[bond.from];
    const endAtom = atoms[bond.to];
    const start = new THREE.Vector3(...startAtom.pos);
    const end = new THREE.Vector3(...endAtom.pos);
    const mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
    const direction = new THREE.Vector3().subVectors(end, start);
    const length = direction.length();

    const geometry = new THREE.CylinderGeometry(cylinderRadius, cylinderRadius, length, 8);
    const material = new THREE.MeshPhysicalMaterial({
      color: 0xa1a1aa,
      roughness: 0.4,
      metalness: 0.1,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(mid);

    const axis = new THREE.Vector3(0, 1, 0);
    const quaternion = new THREE.Quaternion().setFromUnitVectors(axis, direction.clone().normalize());
    mesh.setRotationFromQuaternion(quaternion);
    group.add(mesh);
  });

  const center = new THREE.Vector3();
  atoms.forEach(a => center.add(new THREE.Vector3(...a.pos)));
  center.divideScalar(atoms.length);
  group.children.forEach(child => child.position.sub(center));

  return group;
}

export default function MoleculeScene() {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const frameRef = useRef<number>(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.innerHTML = '';

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 500;

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 0, 13);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
    directionalLight1.position.set(6, 6, 6);
    scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight2.position.set(-6, -4, -4);
    scene.add(directionalLight2);

    const caffeineGroup = buildMoleculeGroup(CAFFEINE_ATOMS, CAFFEINE_BONDS, 0.06);
    caffeineGroup.position.set(0, 0.2, 0);
    scene.add(caffeineGroup);

    const benzeneGroup = buildMoleculeGroup(BENZENE_ATOMS, BENZENE_BONDS, 0.04);
    benzeneGroup.position.set(4.5, 2.2, -3.5);
    benzeneGroup.scale.set(0.75, 0.75, 0.75);
    scene.add(benzeneGroup);

    const waterGroup = buildMoleculeGroup(WATER_ATOMS, WATER_BONDS, 0.04);
    waterGroup.position.set(-4.8, -1.8, -2.5);
    waterGroup.scale.set(0.85, 0.85, 0.85);
    scene.add(waterGroup);

    const particleCount = 180;
    const particleGeometry = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    const particleScales = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      const radius = 3.5 + Math.random() * 8.5;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);

      particlePositions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      particlePositions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      particlePositions[i * 3 + 2] = radius * Math.cos(phi) - 2.0;

      particleScales[i] = Math.random() * 0.08 + 0.03;
    }

    particleGeometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

    const particleMaterial = new THREE.PointsMaterial({
      color: 0x71717a,
      size: 0.12,
      transparent: true,
      opacity: 0.45,
      blending: THREE.NormalBlending,
    });

    const particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);

    const ringGeo = new THREE.RingGeometry(3.6, 3.63, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x94a3b8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.25,
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = Math.PI / 3;
    ringMesh.rotation.y = Math.PI / 6;
    scene.add(ringMesh);

    let mouseX = 0;
    let mouseY = 0;

    const onMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
      mouseY = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
    };
    container.addEventListener('mousemove', onMouseMove);

    let clock = new THREE.Clock();

    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      caffeineGroup.rotation.y += 0.0035;
      caffeineGroup.rotation.x += 0.0015;
      caffeineGroup.rotation.y += mouseX * 0.008;
      caffeineGroup.rotation.x += mouseY * 0.004;

      benzeneGroup.rotation.x = Math.sin(elapsedTime * 0.5) * 0.4;
      benzeneGroup.rotation.y += 0.006;
      benzeneGroup.position.y = 2.2 + Math.sin(elapsedTime * 0.7) * 0.3;

      waterGroup.rotation.z += 0.008;
      waterGroup.rotation.y += 0.005;
      waterGroup.position.y = -1.8 + Math.cos(elapsedTime * 0.8) * 0.25;

      particles.rotation.y = elapsedTime * 0.02 + mouseX * 0.05;
      particles.rotation.x = Math.sin(elapsedTime * 0.01) * 0.1 + mouseY * 0.03;

      ringMesh.rotation.z = elapsedTime * 0.08;

      renderer.render(scene, camera);
    };

    animate();

    const onResize = () => {
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(frameRef.current);
      container.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('resize', onResize);
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '100%',
        position: 'absolute',
        top: 0,
        left: 0,
        pointerEvents: 'auto',
        zIndex: 0,
      }}
    />
  );
}
