import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import BrandingPage from '../pages/BrandingPage';
import { AgencyProvider } from '../context/AgencyContext';

const renderBranding = () => {
  return render(
    <AgencyProvider>
      <BrandingPage />
    </AgencyProvider>
  );
};

describe('Branding configurator', () => {
  it('propagates theme overrides across the UI', () => {
    renderBranding();

    const primaryColorInput = screen.getByLabelText('Primary color') as HTMLInputElement;
    const accentColorInput = screen.getByLabelText('Accent color') as HTMLInputElement;

    fireEvent.change(primaryColorInput, { target: { value: '#123456' } });
    fireEvent.change(accentColorInput, { target: { value: '#ff3366' } });

    fireEvent.click(screen.getByRole('button', { name: /save branding/i }));

    const preview = screen.getByTestId('theme-preview');
    expect(preview).toHaveStyle({ borderTopColor: '#123456' });

    const computedPrimary = document.documentElement.style.getPropertyValue('--color-primary');
    expect(computedPrimary).toBe('#123456');

    const computedAccent = document.documentElement.style.getPropertyValue('--color-accent');
    expect(computedAccent).toBe('#ff3366');
  });
});
