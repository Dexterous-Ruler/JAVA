import { describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ClientsPage from '../pages/ClientsPage';
import { AgencyProvider } from '../context/AgencyContext';

const renderClients = () =>
  render(
    <AgencyProvider>
      <ClientsPage />
    </AgencyProvider>
  );

describe('Client management dashboard', () => {
  it('supports inviting clients and assigning roles', async () => {
    const user = userEvent.setup();
    renderClients();

    await user.type(screen.getByLabelText('Client name'), 'Acme Ventures');
    await user.type(screen.getByLabelText('Email'), 'founder@acme.com');
    await user.selectOptions(screen.getByLabelText('Role'), 'Editor');
    const workspaceSelect = screen.getByLabelText('Workspace');
    const retailOption = screen.getByRole('option', { name: 'Retail Collective' });
    await user.selectOptions(workspaceSelect, retailOption);

    await user.click(screen.getByRole('button', { name: /send invite/i }));

    const inviteFeedback = await screen.findByText('Invitation sent!');
    expect(inviteFeedback).toBeInTheDocument();

    const invitedClient = await screen.findByText('Acme Ventures');
    const invitedRow = invitedClient.closest('[role="row"]');
    expect(invitedRow).toBeTruthy();
    const statusCell = within(invitedRow as HTMLElement).getByText(/Invited/i);
    expect(statusCell).toBeInTheDocument();

    const roleSelect = within(invitedRow as HTMLElement).getByLabelText('Change role for Acme Ventures');
    await user.selectOptions(roleSelect, 'Admin');

    const updatedRoleBadge = await within(invitedRow as HTMLElement).findByText('Admin');
    expect(updatedRoleBadge).toBeInTheDocument();

    const activeBadge = await within(invitedRow as HTMLElement).findByText('Active');
    expect(activeBadge).toBeInTheDocument();
  });
});
