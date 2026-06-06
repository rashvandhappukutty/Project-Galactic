// frontend/src/components/GalaxyExplorer.tsx
import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

interface Star {
  id?: string;
  star_id?: string;
  name: string;
  x: number;
  y: number;
  z: number;
  star_type: string;
  luminosity?: number;
}

interface GalaxyExplorerProps {
  stars: Star[];
  onSelectStar: (star: Star) => void;
  selectedStar: Star | null;
}

export const GalaxyExplorer: React.FC<GalaxyExplorerProps> = ({
  stars,
  onSelectStar,
  selectedStar,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [hoveredStar, setHoveredStar] = useState<Star | null>(null);

  useEffect(() => {
    if (!mountRef.current || stars.length === 0) return;

    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;

    // 1. Scene Setup
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x05070a, 0.015);

    // 2. Camera Setup
    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(0, 35, 55);

    // 3. Renderer Setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    mountRef.current.appendChild(renderer.domElement);

    // 4. Controls Setup
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxDistance = 150;
    controls.minDistance = 5;

    // 5. Lighting Setup
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x3b82f6, 1.5, 100);
    pointLight.position.set(0, 10, 0);
    scene.add(pointLight);

    // 6. Spectral Type Color Mapping
    const getColorForType = (type: string) => {
      const char = type.charAt(0).toUpperCase();
      switch (char) {
        case "O": return 0x3b82f6; // Blue
        case "B": return 0x60a5fa; // Light Blue
        case "A": return 0xffffff; // White
        case "F": return 0xfef08a; // Light Yellow
        case "G": return 0xeab308; // Yellow
        case "K": return 0xf97316; // Orange
        case "M": return 0xef4444; // Red
        default: return 0xa855f7; // Unknown / Purple
      }
    };

    // 7. Add Stars
    const starGeometry = new THREE.SphereGeometry(0.2, 8, 8);
    const starMeshes: THREE.Mesh[] = [];

    // Scale coordinates to fit view
    const xs = stars.map((s) => s.x);
    const zs = stars.map((s) => s.z);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minZ = Math.min(...zs), maxZ = Math.max(...zs);

    const scale = (val: number, min: number, max: number, targetMax: number) => {
      if (max === min) return 0;
      return ((val - min) / (max - min) - 0.5) * targetMax * 2;
    };

    stars.forEach((star) => {
      const color = getColorForType(star.star_type);
      const starMaterial = new THREE.MeshBasicMaterial({ color });
      const mesh = new THREE.Mesh(starGeometry, starMaterial);

      const x = scale(star.x, minX, maxX, 25);
      const y = star.y ? scale(star.y, -100, 100, 5) : (Math.random() - 0.5) * 4;
      const z = scale(star.z, minZ, maxZ, 25);

      mesh.position.set(x, y, z);
      mesh.userData = { starData: star };
      scene.add(mesh);
      starMeshes.push(mesh);
    });

    // 8. Glow Ring for Selected Star
    const ringGeo = new THREE.RingGeometry(0.5, 0.6, 16);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x3b82f6, side: THREE.DoubleSide });
    const selectionRing = new THREE.Mesh(ringGeo, ringMat);
    selectionRing.rotation.x = Math.PI / 2;
    selectionRing.visible = false;
    scene.add(selectionRing);

    // Update selection ring position
    if (selectedStar) {
      const matchedMesh = starMeshes.find(
        (m) => m.userData.starData.name === selectedStar.name
      );
      if (matchedMesh) {
        selectionRing.position.copy(matchedMesh.position);
        selectionRing.visible = true;
      }
    }

    // 9. Raycasting (Interaction)
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onPointerMove = (event: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(starMeshes);

      if (intersects.length > 0) {
        const hovered = intersects[0].object.userData.starData as Star;
        setHoveredStar(hovered);
        document.body.style.cursor = "pointer";
      } else {
        setHoveredStar(null);
        document.body.style.cursor = "default";
      }
    };

    const onClick = (event: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(starMeshes);

      if (intersects.length > 0) {
        const selected = intersects[0].object.userData.starData as Star;
        onSelectStar(selected);
        
        selectionRing.position.copy(intersects[0].object.position);
        selectionRing.visible = true;
      }
    };

    renderer.domElement.addEventListener("mousemove", onPointerMove);
    renderer.domElement.addEventListener("click", onClick);

    // 10. Animation Loop
    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      
      // Rotate scene slowly
      scene.rotation.y += 0.0004;

      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // 11. Resize Handler
    const handleResize = () => {
      if (!mountRef.current) return;
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    // 12. Cleanup
    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
      if (renderer.domElement && mountRef.current) {
        renderer.domElement.removeEventListener("mousemove", onPointerMove);
        renderer.domElement.removeEventListener("click", onClick);
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [stars, onSelectStar]);

  // Handle selected star changes externally (e.g. search select)
  useEffect(() => {
    if (!selectedStar) return;
  }, [selectedStar]);

  return (
    <div className="relative w-full h-full min-h-[400px] glass-panel rounded-xl overflow-hidden">
      <div ref={mountRef} className="w-full h-full absolute inset-0" />
      
      {/* Visual map Overlay HUD */}
      <div className="absolute top-4 left-4 pointer-events-none bg-space-dark/80 px-3 py-2 rounded border border-white/10 text-xs font-mono uppercase tracking-wider text-blue-400">
        Galaxy Map Active | Zoom/Rotate Enabled
      </div>

      {hoveredStar && (
        <div className="absolute bottom-4 left-4 bg-space-dark/95 border border-blue-500/30 p-3 rounded-lg pointer-events-none font-mono text-xs shadow-lg glass-panel-glow">
          <p className="text-blue-400 font-bold text-sm">{hoveredStar.name}</p>
          <p>Spectral Class: <span className="text-yellow-400">{hoveredStar.star_type}</span></p>
          <p>Coordinates: {hoveredStar.x.toFixed(1)}, {hoveredStar.y?.toFixed(1) || 0}, {hoveredStar.z.toFixed(1)}</p>
        </div>
      )}
    </div>
  );
};
