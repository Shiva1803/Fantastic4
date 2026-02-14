/**
 * Smooth scroll component using GSAP ScrollSmoother
 * Provides buttery smooth scrolling experience
 */

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface SmoothScrollProps {
  children: React.ReactNode;
}

export default function SmoothScroll({ children }: SmoothScrollProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Enable smooth scrolling with GSAP
    const ctx = gsap.context(() => {
      // Smooth scroll behavior
      gsap.to(window, {
        scrollBehavior: 'smooth',
        duration: 0.5,
      });

      // Add scroll-triggered animations
      gsap.utils.toArray('.fade-in-scroll').forEach((element: any) => {
        gsap.from(element, {
          scrollTrigger: {
            trigger: element,
            start: 'top 80%',
            end: 'top 20%',
            toggleActions: 'play none none reverse',
          },
          opacity: 0,
          y: 30,
          duration: 0.8,
          ease: 'power2.out',
        });
      });
    }, scrollRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={scrollRef} className="smooth-scroll-wrapper">
      {children}
    </div>
  );
}
