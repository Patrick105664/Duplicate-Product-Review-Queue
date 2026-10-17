import React from "react";

export default function BluetoothSpeaker() {
  return (
    <svg viewBox="0 0 72 72" role="img" aria-label="Compact Bluetooth speaker">
      <defs>
        <linearGradient id="speaker-body" x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="#ad98c2" />
          <stop offset=".55" stopColor="#846d9b" />
          <stop offset="1" stopColor="#69577e" />
        </linearGradient>
        <linearGradient id="speaker-grill" x1="0" y1="0" x2="0" y2="1">
          <stop stopColor="#e5dcef" />
          <stop offset="1" stopColor="#c5b5d4" />
        </linearGradient>
        <filter id="speaker-shadow" x="-30%" y="-30%" width="160%" height="180%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#49365b" floodOpacity=".22" />
        </filter>
      </defs>
      <g filter="url(#speaker-shadow)">
        <rect x="10" y="21" width="52" height="32" rx="15" fill="url(#speaker-body)" stroke="#604e73" strokeWidth="1" />
        <path d="M19 25v24M53 25v24" stroke="#d8cbe4" strokeOpacity=".55" strokeWidth="1" />
        <rect x="19" y="25" width="34" height="24" rx="11" fill="url(#speaker-grill)" />
        <path d="M23 30h26M21 34h30M20 38h32M22 42h28M25 46h22" stroke="#9885a8" strokeOpacity=".6" strokeWidth="1" />
        <circle cx="36" cy="17" r="1.5" fill="#fff" />
        <path d="M35 13v8l4-4z" fill="#f3ecfa" />
        <path d="M17 24c6-4 31-5 38 0" fill="none" stroke="#fff" strokeOpacity=".33" strokeWidth="1.5" strokeLinecap="round" />
      </g>
    </svg>
  );
}
