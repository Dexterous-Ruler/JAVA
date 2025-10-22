import { FormEvent, useState } from 'react';
import { useAgency } from '../hooks/useAgency';
import './InviteClientForm.css';

const InviteClientForm = () => {
  const { inviteClient, roles, workspaces } = useAgency();
  const [formState, setFormState] = useState({
    name: '',
    email: '',
    role: roles[roles.length - 1] ?? 'Viewer',
    workspaceId: workspaces[0]?.id ?? ''
  });
  const [feedbackMessage, setFeedbackMessage] = useState('');

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setFormState((prev) => ({
      ...prev,
      [name]: value
    }));
    setFeedbackMessage('');
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!formState.name || !formState.email || !formState.workspaceId) {
      setFeedbackMessage('Name, email, and workspace are required to send an invitation.');
      return;
    }

    inviteClient(formState);
    setFormState({
      name: '',
      email: '',
      role: roles[roles.length - 1] ?? 'Viewer',
      workspaceId: workspaces[0]?.id ?? ''
    });
    setFeedbackMessage('Invitation sent!');
  };

  return (
    <form className="invite-form" onSubmit={handleSubmit} data-testid="invite-form">
      <div className="invite-form__grid">
        <div className="form-group">
          <label htmlFor="invite-name">Client name</label>
          <input id="invite-name" name="name" value={formState.name} onChange={handleChange} placeholder="Acme Corp" />
        </div>
        <div className="form-group">
          <label htmlFor="invite-email">Email</label>
          <input
            id="invite-email"
            name="email"
            type="email"
            value={formState.email}
            onChange={handleChange}
            placeholder="owner@company.com"
          />
        </div>
        <div className="form-group">
          <label htmlFor="invite-role">Role</label>
          <select id="invite-role" name="role" value={formState.role} onChange={handleChange}>
            {roles.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="invite-workspace">Workspace</label>
          <select
            id="invite-workspace"
            name="workspaceId"
            value={formState.workspaceId}
            onChange={handleChange}
          >
            {workspaces.map((workspace) => (
              <option key={workspace.id} value={workspace.id}>
                {workspace.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="invite-form__footer">
        <button type="submit" className="btn btn--primary" data-testid="invite-submit">
          Send invite
        </button>
        {feedbackMessage ? <span className="invite-form__feedback">{feedbackMessage}</span> : null}
      </div>
    </form>
  );
};

export default InviteClientForm;
