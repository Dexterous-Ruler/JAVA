import BrandingConfigurator from '../components/BrandingConfigurator';
import CustomDomainManager from '../components/CustomDomainManager';
import ThemePreview from '../components/ThemePreview';
import './BrandingPage.css';

const BrandingPage = () => {
  return (
    <section className="branding-page">
      <div className="branding-page__grid">
        <BrandingConfigurator />
        <ThemePreview />
      </div>
      <CustomDomainManager />
    </section>
  );
};

export default BrandingPage;
