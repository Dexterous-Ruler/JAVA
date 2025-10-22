import { FormEvent, useEffect, useState } from 'react';
import { useAgency } from '../hooks/useAgency';
import { BrandingTheme } from '../types';

const BrandingConfigurator = () => {
  const { branding, updateBranding } = useAgency();
  const [formState, setFormState] = useState<BrandingTheme>(branding);
  const [lastSavedAt, setLastSavedAt] = useState<string>('');

  useEffect(() => {
    setFormState(branding);
  }, [branding]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setFormState((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    updateBranding(formState);
    setLastSavedAt(new Date().toLocaleTimeString());
  };

  return (
    <section className="panel" aria-labelledby="branding-configurator-title">
      <div className="panel__header">
        <div>
          <h2 className="panel__title" id="branding-configurator-title">
            Branding & Theme
          </h2>
          <p className="panel__subtitle">Customize the white-label experience for clients.</p>
        </div>
        {lastSavedAt ? <span className="panel__meta">Saved · {lastSavedAt}</span> : null}
      </div>

      <form onSubmit={handleSubmit} className="panel__form" data-testid="branding-form">
        <div className="form-group">
          <label htmlFor="logoUrl">Logo URL</label>
          <input
            id="logoUrl"
            name="logoUrl"
            value={formState.logoUrl}
            onChange={handleInputChange}
            placeholder="https://your-logo.example.com/logo.svg"
          />
        </div>

        <div className="form-group form-group--inline">
          <div>
            <label htmlFor="primaryColor">Primary color</label>
            <input id="primaryColor" name="primaryColor" type="color" value={formState.primaryColor} onChange={handleInputChange} />
          </div>
          <div>
            <label htmlFor="secondaryColor">Secondary color</label>
            <input
              id="secondaryColor"
              name="secondaryColor"
              type="color"
              value={formState.secondaryColor}
              onChange={handleInputChange}
            />
          </div>
          <div>
            <label htmlFor="accentColor">Accent color</label>
            <input id="accentColor" name="accentColor" type="color" value={formState.accentColor} onChange={handleInputChange} />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="themeName">Theme style</label>
          <select id="themeName" name="themeName" value={formState.themeName} onChange={handleInputChange}>
            <option value="Modern">Modern</option>
            <option value="Minimal">Minimal</option>
            <option value="Classic">Classic</option>
          </select>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn--primary">
            Save branding
          </button>
          <button type="button" className="btn btn--ghost" onClick={() => setFormState(branding)}>
            Reset
          </button>
        </div>
      </form>
    </section>
  );
};

export default BrandingConfigurator;
