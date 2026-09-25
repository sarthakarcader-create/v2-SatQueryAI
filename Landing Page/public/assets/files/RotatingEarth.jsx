import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function RotatingEarth() {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const earthRef = useRef(null);
  const glowRef = useRef(null);

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 2.5;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true, 
      alpha: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setClearColor(0x000000, 0);
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Create Earth geometry
    const geometry = new THREE.IcosahedronGeometry(1, 64);

    // Create canvas texture for Earth
    const canvas = document.createElement('canvas');
    canvas.width = 2048;
    canvas.height = 1024;
    const ctx = canvas.getContext('2d');

    // Draw Earth texture
    // Ocean
    ctx.fillStyle = '#1a4d7a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Land masses (simplified continents)
    ctx.fillStyle = '#2d8a3d';
    
    // North America
    ctx.fillRect(100, 200, 150, 120);
    // South America
    ctx.fillRect(200, 350, 80, 120);
    // Europe
    ctx.fillRect(500, 150, 100, 80);
    // Africa
    ctx.fillRect(600, 300, 120, 150);
    // Asia
    ctx.fillRect(800, 150, 250, 180);
    // Australia
    ctx.fillRect(1100, 500, 80, 100);
    
    // Add some cloud effect
    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
    for (let i = 0; i < 50; i++) {
      const x = Math.random() * canvas.width;
      const y = Math.random() * canvas.height;
      const size = Math.random() * 50 + 20;
      ctx.fillRect(x, y, size, size * 0.3);
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.magFilter = THREE.LinearFilter;
    texture.minFilter = THREE.LinearMipmapLinearFilter;

    // Earth material
    const material = new THREE.MeshPhongMaterial({
      map: texture,
      shininess: 5,
      emissive: 0x112244,
    });

    const earth = new THREE.Mesh(geometry, material);
    scene.add(earth);
    earthRef.current = earth;

    // Add glow effect
    const glowGeometry = new THREE.IcosahedronGeometry(1.05, 64);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0x4488ff,
      transparent: true,
      opacity: 0.15,
      wireframe: false,
    });
    const glow = new THREE.Mesh(glowGeometry, glowMaterial);
    scene.add(glow);
    glowRef.current = glow;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(5, 3, 5);
    scene.add(pointLight);

    // Stars in background (small)
    const starsGeometry = new THREE.BufferGeometry();
    const starCount = 500;
    const positions = new Float32Array(starCount * 3);

    for (let i = 0; i < starCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 100;
      positions[i + 1] = (Math.random() - 0.5) * 100;
      positions[i + 2] = (Math.random() - 0.5) * 100;
    }

    starsGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const starsMaterial = new THREE.PointsMaterial({
      size: 0.1,
      sizeAttenuation: true,
      color: 0xffffff,
      transparent: true,
      opacity: 0.6,
    });

    const stars = new THREE.Points(starsGeometry, starsMaterial);
    scene.add(stars);

    // Handle window resize
    const handleResize = () => {
      if (!mountRef.current) return;
      const width = mountRef.current.clientWidth;
      const height = mountRef.current.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);

    // Mouse tracking
    let mouseX = 0;
    let mouseY = 0;
    let targetRotationX = 0;
    let targetRotationY = 0;

    const handleMouseMove = (e) => {
      mouseX = (e.clientX / window.innerWidth) * 2 - 1;
      mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
      targetRotationY = mouseX * 0.5;
      targetRotationX = mouseY * 0.5;
    };

    window.addEventListener('mousemove', handleMouseMove);

    // Animation loop
    let animationId;
    const animate = () => {
      animationId = requestAnimationFrame(animate);

      // Auto-rotate Earth
      if (earthRef.current) {
        earthRef.current.rotation.y += 0.0003;
        earthRef.current.rotation.x += targetRotationX * 0.05;
        earthRef.current.rotation.y += targetRotationY * 0.05;
        
        targetRotationX *= 0.95;
        targetRotationY *= 0.95;
      }

      // Glow pulse
      if (glowRef.current) {
        glowRef.current.rotation.copy(earth.rotation);
        glowRef.current.material.opacity = 0.15 + Math.sin(Date.now() * 0.001) * 0.05;
      }

      renderer.render(scene, camera);
    };

    animate();

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationId);
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
      geometry.dispose();
      material.dispose();
      texture.dispose();
      glowGeometry.dispose();
      glowMaterial.dispose();
      starsGeometry.dispose();
      starsMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    />
  );
}
