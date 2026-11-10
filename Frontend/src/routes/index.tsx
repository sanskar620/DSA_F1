import { createFileRoute } from "@tanstack/react-router";
import { StrategyDashboard } from "@/components/strategy-dashboard";

// No head() here: the home route inherits title/description/og/twitter from
// __root.tsx, and ships no og:image so serve-time hosting can inject the
// project's social preview (explicit og:image or latest screenshot).
export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "F1 StrategyIQ — Race Strategy Intelligence" },
      { name: "description", content: "Interactive Formula 1 race strategy analytics, tyre intelligence, optimization and pit-wall decision support." },
      { property: "og:title", content: "F1 StrategyIQ — Race Strategy Intelligence" },
      { property: "og:description", content: "Analyze race pace, compare tyre strategies and replay pit-wall decisions." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

// IMPORTANT: Replace this placeholder. See ./README.md for routing conventions.
function Index() {
  return <StrategyDashboard />;
}
