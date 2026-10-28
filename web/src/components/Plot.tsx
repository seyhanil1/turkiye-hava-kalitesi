"use client";

import dynamic from "next/dynamic";
import type { PlotParams } from "react-plotly.js";
import type { Layout } from "plotly.js";

// Plotly yalnızca tarayıcıda yüklenir (büyük bir paket olduğu için ayrı parçaya bölünür)
const PlotlyPlot = dynamic(
  async () => {
    const [{ default: Plotly }, { default: createPlotlyComponent }] = await Promise.all([
      import("plotly.js-dist-min"),
      import("react-plotly.js/factory"),
    ]);
    return createPlotlyComponent(Plotly);
  },
  {
    ssr: false,
    loading: () => <div className="h-full min-h-40 w-full animate-pulse rounded-lg bg-panel-2" />,
  },
);

const BASE_LAYOUT: Partial<Layout> = {
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: { family: "var(--font-jakarta), sans-serif", color: "#cbd5e1", size: 11 },
  margin: { l: 50, r: 20, t: 20, b: 40 },
  separators: ",.",
  hoverlabel: { bgcolor: "#021626", font: { color: "#ffffff", size: 11 } },
  xaxis: { gridcolor: "#093452", zerolinecolor: "#093452", tickfont: { color: "#94a3b8", size: 10 } },
  yaxis: { gridcolor: "#093452", zerolinecolor: "#093452", tickfont: { color: "#94a3b8", size: 10 } },
  legend: { font: { color: "#cbd5e1", size: 11 }, bgcolor: "rgba(3,27,46,0.6)" },
};

type Props = Omit<PlotParams, "layout"> & { layout?: Partial<Layout>; height?: number };

export default function Plot({ layout, height = 360, config, style, ...rest }: Props) {
  const merged: Partial<Layout> = {
    ...BASE_LAYOUT,
    ...layout,
    xaxis: { ...BASE_LAYOUT.xaxis, ...layout?.xaxis },
    yaxis: { ...BASE_LAYOUT.yaxis, ...layout?.yaxis },
    height,
    autosize: true,
  };
  return (
    <div style={{ height }} className="w-full">
      <PlotlyPlot
        {...rest}
        layout={merged}
        config={{ displayModeBar: false, responsive: true, locale: "tr", ...(config ?? {}) }}
        style={{ width: "100%", height: "100%", ...style }}
        useResizeHandler
      />
    </div>
  );
}
