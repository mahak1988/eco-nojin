import { useState, type VideoHTMLAttributes } from "react";

interface Props extends VideoHTMLAttributes<HTMLVideoElement> {
  videoSrc: string;
  posterSrc: string;
  fallbackSrc?: string;
  className?: string;
  overlayClassName?: string;
  children?: React.ReactNode;
}

export default function HeroVideo({
  videoSrc,
  posterSrc,
  fallbackSrc,
  className = "",
  overlayClassName = "",
  children,
  ...rest
}: Props) {
  const [videoFailed, setVideoFailed] = useState(false);

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {!videoFailed ? (
        <video
          autoPlay
          muted
          loop
          playsInline
          poster={posterSrc}
          onError={() => setVideoFailed(true)}
          className="absolute inset-0 h-full w-full object-cover"
          {...rest}
        >
          <source src={videoSrc} type="video/webm" />
          <source src={videoSrc.replace(/\.webm$/, ".mp4")} type="video/mp4" />
        </video>
      ) : fallbackSrc ? (
        <img
          src={fallbackSrc}
          alt=""
          className="absolute inset-0 h-full w-full object-cover"
        />
      ) : (
        <img
          src={posterSrc}
          alt=""
          className="absolute inset-0 h-full w-full object-cover"
        />
      )}
      {/* gradient overlay */}
      <div className={`absolute inset-0 bg-gradient-to-b from-black/50 via-black/30 to-black/70 ${overlayClassName}`} />
      {children && (
        <div className="relative z-10 flex h-full flex-col items-center justify-center">
          {children}
        </div>
      )}
    </div>
  );
}
