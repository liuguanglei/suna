'use client';

import Image from 'next/image';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

interface KortixLogoProps {
  size?: number;
}
export function KortixLogo({ size = 24 }: KortixLogoProps) {
  const { theme, systemTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // After mount, we can access the theme
  useEffect(() => {
    setMounted(true);
  }, []);

  const shouldInvert =
    mounted &&
    (theme === 'dark' || (theme === 'system' && systemTheme === 'dark'));

  return (
    <Image
      src={`${process.env.NEXT_PUBLIC_BASE_PATH}/ic_kongming_logo.png`}
      alt="Kortix"
      width={size}
      height={size}
      className={`${mounted && theme === 'dark' ? 'invert' : ''} flex-shrink-0`}
    />
  );
}
