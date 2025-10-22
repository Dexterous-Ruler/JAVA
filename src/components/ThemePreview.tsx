import { useAgency } from '../hooks/useAgency';
import './ThemePreview.css';

const ThemePreview = () => {
  const { branding, customDomain } = useAgency();

  return (
    <section className="panel theme-preview" aria-labelledby="theme-preview-title">
      <div className="panel__header">
        <div>
          <h2 className="panel__title" id="theme-preview-title">
            Live preview
          </h2>
          <p className="panel__subtitle">Review how clients experience your white-label portal.</p>
        </div>
        <span className="theme-preview__domain" data-testid="custom-domain-status">
          {customDomain.domain} · {customDomain.status}
        </span>
      </div>

      <div className="theme-preview__canvas" data-testid="theme-preview" style={{ borderTopColor: branding.primaryColor }}>
        <header className="theme-preview__header" style={{ background: branding.primaryColor }}>
          <img src={branding.logoUrl} alt="Preview logo" className="theme-preview__logo" />
          <span className="theme-preview__badge" style={{ background: branding.accentColor }}>
            {branding.themeName}
          </span>
        </header>

        <div className="theme-preview__body">
          <div className="theme-preview__card" style={{ borderColor: branding.secondaryColor }}>
            <p className="theme-preview__card-label">Engagement rate</p>
            <p className="theme-preview__card-value" style={{ color: branding.primaryColor }}>
              87%
            </p>
            <span className="theme-preview__chip" style={{ background: `${branding.secondaryColor}22`, color: branding.secondaryColor }}>
              +12% WoW
            </span>
          </div>

          <div className="theme-preview__grid">
            <div className="theme-preview__tile" style={{ background: `${branding.primaryColor}11` }}>
              <p>Client satisfaction</p>
              <strong>{branding.themeName === 'Minimal' ? '4.9 / 5' : '4.7 / 5'}</strong>
            </div>
            <div className="theme-preview__tile" style={{ background: `${branding.secondaryColor}11` }}>
              <p>Avg. time to value</p>
              <strong>18 days</strong>
            </div>
            <div className="theme-preview__tile" style={{ background: `${branding.accentColor}11` }}>
              <p>CSAT trend</p>
              <strong>+6.3%</strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ThemePreview;
