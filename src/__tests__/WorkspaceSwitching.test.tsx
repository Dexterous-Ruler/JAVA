import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import { MemoryRouter } from 'react-router-dom';
import { AgencyProvider } from '../context/AgencyContext';

const renderAppAt = (path: string) =>
  render(
    <MemoryRouter initialEntries={[path]}>
      <AgencyProvider>
        <App />
      </AgencyProvider>
    </MemoryRouter>
  );

describe('Workspace switching and metrics', () => {
  it('updates metrics when switching workspaces while keeping aggregated totals', async () => {
    const user = userEvent.setup();
    renderAppAt('/metrics');

    const activeClientsCard = await screen.findByTestId('metric-card-active-clients');
    expect(activeClientsCard).toHaveTextContent('18');

    const totalClientsCard = await screen.findByText('Total clients');
    expect(totalClientsCard.nextElementSibling).toHaveTextContent('39');

    await user.selectOptions(screen.getByLabelText('Active workspace'), 'Fintech Alliance');

    const updatedClientsCard = await screen.findByTestId('metric-card-active-clients');
    expect(updatedClientsCard).toHaveTextContent('9');

    expect(totalClientsCard.nextElementSibling).toHaveTextContent('39');
  });
});
