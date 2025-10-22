import { ChangeEvent } from 'react';
import { useAgency } from '../hooks/useAgency';
import './WorkspaceSwitcher.css';

const WorkspaceSwitcher = () => {
  const { workspaces, currentWorkspaceId, switchWorkspace } = useAgency();

  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    switchWorkspace(event.target.value);
  };

  const currentWorkspace = workspaces.find((workspace) => workspace.id === currentWorkspaceId);

  return (
    <div className="workspace-switcher" data-testid="workspace-switcher">
      <div>
        <label htmlFor="workspace-select" className="workspace-switcher__label">
          Active workspace
        </label>
        <select
          id="workspace-select"
          value={currentWorkspaceId}
          onChange={handleChange}
          className="workspace-switcher__select"
        >
          {workspaces.map((workspace) => (
            <option key={workspace.id} value={workspace.id}>
              {workspace.name}
            </option>
          ))}
        </select>
      </div>
      {currentWorkspace ? (
        <div className="workspace-switcher__summary">
          <div>
            <p className="workspace-switcher__summary-label">Industry</p>
            <p className="workspace-switcher__summary-value">{currentWorkspace.industry}</p>
          </div>
          <div>
            <p className="workspace-switcher__summary-label">Active projects</p>
            <p className="workspace-switcher__summary-value">{currentWorkspace.metrics.activeProjects}</p>
          </div>
          <div>
            <p className="workspace-switcher__summary-label">Utilization</p>
            <p className="workspace-switcher__summary-value">
              {Math.round(currentWorkspace.metrics.utilizationRate * 100)}%
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default WorkspaceSwitcher;
