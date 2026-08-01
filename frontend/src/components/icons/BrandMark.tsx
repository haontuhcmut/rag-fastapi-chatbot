export default function BrandMark({
  size = 20,
  className = "",
  wedge = "triple",
  showCheck = true,
  ringRatio = 0.7,
  wedgeRatio = 0.25,
  ringColor = "#1976D2",
  wedgeColor = "#FFD700",
}: {
  size?: number;
  className?: string;
  wedge?: "single" | "triple";
  showCheck?: boolean;
  ringRatio?: number;
  wedgeRatio?: number;
  ringColor?: string;
  wedgeColor?: string;
}) {
  // QUATEST3-style mark: blue ring with yellow wedge tail.
  // Supports single or triple wedge variants; default is single to match the provided sample.
  const cx = 16;
  const cy = 16;
  const R = 13; // outer ring radius
  // Compute inner radius from desired ring area ratio: ringArea = 1 - (r^2/R^2)
  const innerR = Math.max(
    5.5,
    Math.min(R - 1, R * Math.sqrt(1 - Math.max(0.1, Math.min(0.9, ringRatio)))),
  );
  // Compute wedge length from ratio of diameter
  const wedgeLen = Math.max(
    5.5,
    2 * R * Math.max(0.05, Math.min(0.3, wedgeRatio)),
  );

  // Polar helpers for anchored slats (emanating from ring near ~5 o'clock)
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const polar = (r: number, deg: number) => {
    const rad = toRad(deg);
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  };
  // Arc parameters for donut segments: 10% of circle = 36°
  const centerAngleDeg = 400; // keep orientation similar to previous (~40° modulo 360)
  const segmentWidthDeg = 36; // 10% of 360°
  const arcSegmentPath = (startDeg: number, endDeg: number) => {
    const outerStart = polar(R, startDeg);
    const outerEnd = polar(R, endDeg);
    const innerEnd = polar(innerR, endDeg);
    const innerStart = polar(innerR, startDeg);
    const sweepOuter = 1; // clockwise
    const sweepInner = 0; // counter-clockwise
    const largeArc = Math.abs(endDeg - startDeg) > 180 ? 1 : 0;
    return [
      `M ${outerStart.x} ${outerStart.y}`,
      `A ${R} ${R} 0 ${largeArc} ${sweepOuter} ${outerEnd.x} ${outerEnd.y}`,
      `L ${innerEnd.x} ${innerEnd.y}`,
      `A ${innerR} ${innerR} 0 ${largeArc} ${sweepInner} ${innerStart.x} ${innerStart.y}`,
      "Z",
    ].join(" ");
  };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
      focusable="false"
    >
      {/* Blue ring */}
      <circle cx={cx} cy={cy} r={R} fill={ringColor} />
      <circle cx={cx} cy={cy} r={innerR} fill="white" />

      {/* Inner check mark (optional) */}
      {showCheck && (
        <path
          d="M12.6 16.4 L14.7 18.7 L19.4 13.6"
          fill="none"
          stroke={ringColor}
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      )}

      {wedge === "single" ? (
        // Single segment of 10%
        <path
          d={arcSegmentPath(
            centerAngleDeg - segmentWidthDeg / 2,
            centerAngleDeg + segmentWidthDeg / 2,
          )}
          fill={wedgeColor}
        />
      ) : (
        // Triple segments: three contiguous 10% arcs totaling 30%
        <>
          <path
            d={arcSegmentPath(
              centerAngleDeg - segmentWidthDeg * 1.5,
              centerAngleDeg - segmentWidthDeg * 0.5,
            )}
            fill={wedgeColor}
          />
          <path
            d={arcSegmentPath(
              centerAngleDeg - segmentWidthDeg * 0.5,
              centerAngleDeg + segmentWidthDeg * 0.5,
            )}
            fill={wedgeColor}
          />
          <path
            d={arcSegmentPath(
              centerAngleDeg + segmentWidthDeg * 0.5,
              centerAngleDeg + segmentWidthDeg * 1.5,
            )}
            fill={wedgeColor}
          />
        </>
      )}
    </svg>
  );
}
