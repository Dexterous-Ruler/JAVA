import AggregatedMetrics from '../components/AggregatedMetrics';
import WorkspaceMetrics from '../components/WorkspaceMetrics';
import './MetricsPage.css';

const MetricsPage = () => {
  return (
    <section className="metrics-page">
      <WorkspaceMetrics />
      <AggregatedMetrics />
    </section>
  );
};

export default MetricsPage;
