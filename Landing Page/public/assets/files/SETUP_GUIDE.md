# Three.js Components Setup Guide

## Installation

### 1. Install Three.js
```bash
npm install three
```

### 2. File Structure
Place the components in your project:
```
src/
└── components/
    └── effects/
        ├── StarfieldBackground.jsx
        └── RotatingEarth.jsx
```

### 3. Update Next.js Configuration (if needed)

In `next.config.js`, add support for Three.js:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { isServer }) => {
    config.module.rules.push({
      test: /three\/examples\/jsm/,
      sideEffects: true,
    });
    return config;
  },
};

module.exports = nextConfig;
```

---

## Component Usage

### StarfieldBackground
**Purpose:** Animated starfield background that covers the entire viewport.

**Props:** None

**Usage:**
```jsx
import StarfieldBackground from '@/components/effects/StarfieldBackground';

export default function Hero() {
  return (
    <section id="home" className="relative min-h-screen overflow-hidden">
      <StarfieldBackground />
      {/* Your content here */}
    </section>
  );
}
```

**Features:**
- 1000 animated stars
- Parallax rotation effect
- Responsive to window resize
- Performance optimized
- Fixed positioning (background only)

---

### RotatingEarth
**Purpose:** Interactive 3D rotating Earth globe with glow effect.

**Props:** None

**Usage:**
```jsx
import RotatingEarth from '@/components/effects/RotatingEarth';

export default function Hero() {
  return (
    <section id="home" className="relative min-h-screen">
      <StarfieldBackground />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-96 h-96">
          <RotatingEarth />
        </div>
      </div>
      {/* Other content */}
    </section>
  );
}
```

**Features:**
- Rotating 3D globe
- Mouse interaction (tilt effect)
- Procedural texture (no external image needed)
- Glow animation pulse
- Realistic lighting
- Background stars
- Responsive sizing

---

## Complete Hero Section Example

```jsx
'use client';

import StarfieldBackground from '@/components/effects/StarfieldBackground';
import RotatingEarth from '@/components/effects/RotatingEarth';
import PrimaryButton from '@/components/buttons/PrimaryButton';

export default function Hero() {
  return (
    <section 
      id="home" 
      className="relative w-full h-screen overflow-hidden flex items-center justify-center"
    >
      {/* Starfield Background */}
      <StarfieldBackground />

      {/* Main Content Grid */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 grid grid-cols-2 gap-8 items-center">
        
        {/* Left Content */}
        <div className="flex flex-col justify-center space-y-6">
          <h1 className="text-5xl md:text-6xl font-bold text-white">
            Welcome to Our Platform
          </h1>
          
          <p className="text-lg text-gray-300">
            Experience the future with our cutting-edge technology
          </p>

          <div className="flex gap-4">
            <PrimaryButton href="#features">
              Explore Features
            </PrimaryButton>
            <PrimaryButton variant="secondary" href="#contact">
              Get Started
            </PrimaryButton>
          </div>
        </div>

        {/* Right Content - Rotating Earth */}
        <div className="flex items-center justify-center h-full">
          <div className="w-80 h-80">
            <RotatingEarth />
          </div>
        </div>
      </div>
    </section>
  );
}
```

---

## Performance Notes

### Optimization Tips:
- **StarfieldBackground** uses `requestAnimationFrame` for smooth 60fps animation
- **RotatingEarth** uses canvas texture (no external image downloads)
- Both components clean up Three.js resources on unmount
- Pixel ratio is set to device ratio for crisp rendering

### Browser Support:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Customization

### StarfieldBackground Customization:

```jsx
// Change star count (in component):
const starCount = 2000; // More stars

// Change rotation speed:
starsRef.current.rotation.x += 0.0001; // Faster rotation
starsRef.current.rotation.y += 0.0002;

// Change background color:
renderer.setClearColor(0x001a4d, 0.1); // Different color
```

### RotatingEarth Customization:

```jsx
// Change rotation speed:
if (earthRef.current) {
  earthRef.current.rotation.y += 0.0005; // Faster
}

// Adjust glow color:
const glowMaterial = new THREE.MeshBasicMaterial({
  color: 0xff6600, // Change to orange glow
  transparent: true,
  opacity: 0.15,
});

// Change Earth size:
camera.position.z = 3.5; // Zoom out more
```

---

## Troubleshooting

### Black Screen?
- Make sure Three.js is installed: `npm install three`
- Check browser console for errors
- Ensure components are not hidden by CSS

### Performance Issues?
- Reduce star count in StarfieldBackground
- Reduce geometry segments (change `64` to `32` in RotatingEarth)
- Check GPU usage in browser DevTools

### Components Not Rendering?
- Verify file paths match your folder structure
- Make sure imports use correct relative paths
- Check that parent container has proper height/width

---

## Next Steps

1. Copy both `.jsx` files to `src/components/effects/`
2. Run `npm install three`
3. Import into your Hero section
4. Adjust sizing and positioning with Tailwind classes
5. Customize colors/speed as needed

You're all set! 🚀
