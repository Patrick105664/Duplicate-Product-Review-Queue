import React from "react";

export default function SmartWatch() {
  return (
    <svg viewBox="0 0 72 72" role="img" aria-label="Sage smart watch">
      <defs>
        <linearGradient id="watch-strap" x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="#a6b69a" />
          <stop offset="1" stopColor="#70836d" />
        </linearGradient>
        <linearGradient id="watch-glass" x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="#514a60" />
          <stop offset="1" stopColor="#252635" />
        </linearGradient>
        <filter id="watch-shadow" x="-30%" y="-30%" width="160%" height="180%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#49365b" floodOpacity=".22" />
        </filter>
      </defs>
      <g filter="url(#watch-shadow)">
        <path d="M27 6h18l4 17H23zM23 49h26l-4 17H27z" fill="url(#watch-strap)" stroke="#61735d" strokeWidth="1" />
        <rect x="18" y="19" width="36" height="34" rx="10" fill="#bac6ad" stroke="#586b58" strokeWidth="1.5" />
        <rect x="21" y="22" width="30" height="28" rx="8" fill="url(#watch-glass)" />
        <path d="M27 39a9 9 0 0 1 18 0" fill="none" stroke="#c5acd9" strokeWidth="2.5" strokeLinecap="round" />
        <path d="M36 32v7l5 3" fill="none" stroke="#f7f0ff" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M25 26c4-4 11-5 17-3" fill="none" stroke="#fff" strokeOpacity=".3" strokeWidth="1.5" strokeLinecap="round" />
        <rect x="54" y="31" width="3" height="9" rx="1.5" fill="#8b9d81" />
      </g>
    </svg>
  );
}
