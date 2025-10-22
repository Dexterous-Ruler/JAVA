import { useAgency } from '../hooks/useAgency';
import './AggregatedMetrics.css';

const AggregatedMetrics = () => {
  const { aggregatedMetrics, workspaces } = useAgency();

  return (
    <section className="panel aggregated-metrics" aria-labelledby="aggregated-metrics-title" data-testid="aggregated-metrics">
      <div className="panel__header">
        <div>
          <h2 className="panel__title" id="aggregated-metrics-title">
            Portfolio overview
          </h2>
          <p className="panel__subtitle">Cross-workspace health signals at a glance.</p>
        </div>
        <span className="panel__meta">{workspaces.length} workspaces</span>
      </div>

      <div className="aggregated-metrics__grid">
        <div className="aggregated-metrics__card">
          <p>Total clients</p>
          <strong>{aggregatedMetrics.totalActiveClients}</strong>
          <span>active this month</span>
        </div>
        <div className="aggregated-metrics__card">
          <p>Active projects</p>
          <strong>{aggregatedMetrics.totalActiveProjects}</strong>
          <span>in flight</span>
        </div>
        <div className="aggregated-metrics__card">
          <p>Average utilization</p>
          <strong>{Math.round(aggregatedMetrics.averageUtilizationRate * 100)}%</strong>
          <span>weighted across teams</span>
        </div>
        <div className="aggregated-metrics__card">
          <p>Avg. satisfaction</p>
          <strong>{aggregatedMetrics.averageSatisfactionScore.toFixed(2)}</strong>
          <span>client happiness index</span>
        </div>
        <div className="aggregated-metrics__card aggregated-metrics__card--span">
          <p>Monthly revenue</p>
          <strong>
            {new Intl.NumberFormat('en-US', {
              style: 'currency',
              currency: 'USD',
              maximumFractionDigits: 0
            }).format(aggregatedMetrics.totalRevenue)}
          </strong>
          <span>Across all workspaces</span>
        </div>
      </div>

      <div className="aggregated-metrics__list">
        {workspaces.map((workspace) => (
          <div key={workspace.id} className="aggregated-metrics__row">
            <div>
              <strong>{workspace.name}</strong>
              <span>{workspace.industry}</span>
            </div>
            <div className="aggregated-metrics__row-metrics">
              <span>{workspace.metrics.activeClients} clients</span>
              <span>{workspace.metrics.activeProjects} projects</span>
              <span>{Math.round(workspace.metrics.utilizationRate * 100)}% utilization</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default AggregatedMetrics;
