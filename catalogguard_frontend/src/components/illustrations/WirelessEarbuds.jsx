import React from "react";

export default function WirelessEarbuds() {
  return (
    <svg viewBox="0 0 72 72" role="img" aria-label="Wireless earbuds and charging case">
      <defs>
        <linearGradient id="earbuds-case" x1="0" y1="0" x2="0" y2="1">
          <stop stopColor="#d7c8e7" />
          <stop offset="1" stopColor="#a68cbe" />
        </linearGradient>
        <linearGradient id="earbuds-stem" x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="#faf8fc" />
          <stop offset="1" stopColor="#c7b8d4" />
        </linearGradient>
        <filter id="earbuds-shadow" x="-30%" y="-30%" width="160%" height="180%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#49365b" floodOpacity=".22" />
        </filter>
      </defs>
      <g filter="url(#earbuds-shadow)">
        <path d="M10 39c0-5 4-9 9-9h34c5 0 9 4 9 9v10c0 6-5 10-11 10H21c-6 0-11-4-11-10z" fill="url(#earbuds-case)" stroke="#9270b8" strokeOpacity=".48" />
        <path d="M10 40h52" stroke="#f8f3fc" strokeOpacity=".9" strokeWidth="2" />
        <circle cx="36" cy="51" r="1.4" fill="#f7edbd" />
        <path d="M24 18a7 7 0 0 1 14 0v6c0 3-2 5-5 5h-2v11h-5V27c-1-1-2-2-2-4z" fill="url(#earbuds-stem)" stroke="#a48cb5" strokeWidth="1.2" />
        <path d="M47 15a7 7 0 0 1 14 0v6c0 3-2 5-5 5h-2v10h-5V24c-1-1-2-2-2-4z" fill="url(#earbuds-stem)" stroke="#a48cb5" strokeWidth="1.2" />
        <path d="M28 17c1-3 4-4 6-2M51 14c1-3 4-4 6-2" fill="none" stroke="#fff" strokeOpacity=".8" strokeWidth="1.5" strokeLinecap="round" />
      </g>
    </svg>
  );
}
