import { FormEvent, useState } from 'react';
import { useAgency } from '../hooks/useAgency';
import './CustomDomainManager.css';

const CustomDomainManager = () => {
  const { customDomain, setCustomDomain } = useAgency();
  const [domainValue, setDomainValue] = useState(customDomain.domain);
  const [feedback, setFeedback] = useState('');

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCustomDomain(domainValue);
    setFeedback('DNS verification pending. We will email you once propagation completes.');
  };

  return (
    <section className="panel domain-manager" aria-labelledby="custom-domain-title">
      <div className="panel__header">
        <div>
          <h2 className="panel__title" id="custom-domain-title">
            Custom domain
          </h2>
          <p className="panel__subtitle">Ship a fully white-labelled experience on your domain.</p>
        </div>
        <span className={`domain-manager__status domain-manager__status--${customDomain.status.toLowerCase()}`}>
          {customDomain.status}
        </span>
      </div>

      <form onSubmit={handleSubmit} className="panel__form" data-testid="custom-domain-form">
        <div className="form-group">
          <label htmlFor="domain">Domain</label>
          <input
            id="domain"
            name="domain"
            value={domainValue}
            placeholder="portal.youragency.com"
            onChange={(event) => setDomainValue(event.target.value.trim())}
          />
        </div>
        <button type="submit" className="btn btn--primary">
          Update domain
        </button>
      </form>

      <div className="domain-manager__helper">
        <h3>DNS requirements</h3>
        <ul>
          <li>Point CNAME record to <strong>wl.agencyhq.com</strong></li>
          <li>Ensure SSL is enabled for full HTTPS coverage</li>
          <li>Propagation typically completes within 15 minutes</li>
        </ul>
      </div>

      {feedback ? <p className="domain-manager__feedback">{feedback}</p> : null}
    </section>
  );
};

export default CustomDomainManager;
