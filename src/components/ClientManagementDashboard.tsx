import { useAgency } from '../hooks/useAgency';
import RoleBadge from './RoleBadge';
import InviteClientForm from './InviteClientForm';
import './ClientManagementDashboard.css';

const ClientManagementDashboard = () => {
  const { clients, roles, assignClientRole, workspaces } = useAgency();

  return (
    <section className="panel clients-dashboard" aria-labelledby="clients-dashboard-title">
      <div className="panel__header">
        <div>
          <h2 className="panel__title" id="clients-dashboard-title">
            Client management
          </h2>
          <p className="panel__subtitle">Control invitations, permissions, and workspace access.</p>
        </div>
        <span className="panel__meta">{clients.length} clients</span>
      </div>

      <InviteClientForm />

      <div className="clients-dashboard__table" role="table">
        <div className="clients-dashboard__row clients-dashboard__row--header" role="row">
          <span role="columnheader">Client</span>
          <span role="columnheader">Email</span>
          <span role="columnheader">Status</span>
          <span role="columnheader">Role</span>
          <span role="columnheader">Workspaces</span>
          <span role="columnheader">Last active</span>
        </div>

        {clients.map((client) => (
          <div className="clients-dashboard__row" role="row" key={client.id} data-testid={`client-row-${client.id}`}>
            <span role="cell" className="clients-dashboard__cell-name">
              <strong>{client.name}</strong>
            </span>
            <span role="cell">{client.email}</span>
            <span role="cell">
              <span className={`status-pill status-pill--${client.status.toLowerCase()}`}>{client.status}</span>
            </span>
            <span role="cell" className="clients-dashboard__cell-role">
              <RoleBadge role={client.role} />
              <label className="sr-only" htmlFor={`role-select-${client.id}`}>
                Change role for {client.name}
              </label>
              <select
                id={`role-select-${client.id}`}
                className="clients-dashboard__role-select"
                value={client.role}
                onChange={(event) => assignClientRole(client.id, event.target.value as typeof client.role)}
                data-testid={`role-select-${client.id}`}
              >
                {roles.map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </select>
            </span>
            <span role="cell" className="clients-dashboard__cell-workspaces">
              {client.workspaces
                .map((workspaceId) => workspaces.find((workspace) => workspace.id === workspaceId)?.name ?? workspaceId)
                .join(', ')}
            </span>
            <span role="cell">{new Date(client.lastActive).toLocaleDateString()}</span>
          </div>
        ))}
      </div>
    </section>
  );
};

export default ClientManagementDashboard;
