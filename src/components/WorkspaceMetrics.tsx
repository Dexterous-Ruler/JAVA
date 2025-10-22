import { useMemo } from 'react';
import { useAgency } from '../hooks/useAgency';
import './WorkspaceMetrics.css';

const WorkspaceMetrics = () => {
  const { workspaces, currentWorkspaceId } = useAgency();

  const workspace = useMemo(
    () => workspaces.find((entry) => entry.id === currentWorkspaceId) ?? workspaces[0],
    [workspaces, currentWorkspaceId]
  );

  if (!workspace) {
    return null;
  }

  const { metrics } = workspace;

  const metricCards = [
    {
      label: 'Active clients',
      value: metrics.activeClients,
      helper: 'connected accounts'
    },
    {
      label: 'Active projects',
      value: metrics.activeProjects,
      helper: 'campaigns in-flight'
    },
    {
      label: 'Utilization rate',
      value: `${Math.round(metrics.utilizationRate * 100)}%`,
      helper: 'delivery capacity'
    },
    {
      label: 'Satisfaction score',
      value: metrics.satisfactionScore.toFixed(1),
      helper: 'NPS adjusted'
    },
    {
      label: 'Monthly revenue',
      value: new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
      }).format(metrics.revenue),
      helper: 'recurring retainers'
    }
  ];

  return (
    <section className="panel workspace-metrics" aria-labelledby="workspace-metrics-title" data-testid="workspace-metrics">
      <div className="panel__header">
        <div>
          <h2 className="panel__title" id="workspace-metrics-title">
            {workspace.name} · metrics
          </h2>
          <p className="panel__subtitle">Real-time performance across this workspace.</p>
        </div>
        <span className="panel__meta">Updated {new Date(metrics.lastUpdated).toLocaleString()}</span>
      </div>

      <div className="metric-grid">
        {metricCards.map((card) => (
          <article key={card.label} className="metric-card" data-testid={`metric-card-${card.label.toLowerCase().replace(/\s+/g, '-')}`}>
            <p className="metric-card__label">{card.label}</p>
            <p className="metric-card__value">{card.value}</p>
            <span className="metric-card__helper">{card.helper}</span>
          </article>
        ))}
      </div>
    </section>
  );
};

export default WorkspaceMetrics;
