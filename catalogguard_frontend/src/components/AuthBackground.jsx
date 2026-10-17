import React, { useEffect, useRef, useState } from "react";
import bgVideo from "../../assets/animated video.mp4";
import "./AuthBackground.css";

export default function AuthBackground() {
  const videoRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(() =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );

  useEffect(() => {
    const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updateMotionPreference = () => setReducedMotion(motionQuery.matches);
    motionQuery.addEventListener("change", updateMotionPreference);
    return () => motionQuery.removeEventListener("change", updateMotionPreference);
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || failed || reducedMotion) return undefined;

    const playVideo = () => {
      if (document.visibilityState === "visible") video.play().catch(() => {});
    };
    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden") video.pause();
      else playVideo();
    };

    playVideo();
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [failed, reducedMotion]);

  return <div className="auth-background" aria-hidden="true">
    {!failed && !reducedMotion && <video
      ref={videoRef}
      className={`auth-background-video ${ready ? "is-ready" : ""}`}
      autoPlay
      muted
      loop
      playsInline
      preload="auto"
      onLoadedData={() => setReady(true)}
      onCanPlay={() => setReady(true)}
      onError={() => setFailed(true)}
    >
      <source src={bgVideo} type="video/mp4" />
    </video>}
    <div className="auth-background-overlay" />
  </div>;
}
