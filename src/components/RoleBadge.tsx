import { ClientRole } from '../types';
import './RoleBadge.css';

interface RoleBadgeProps {
  role: ClientRole;
}

const RoleBadge = ({ role }: RoleBadgeProps) => {
  return <span className={`role-badge role-badge--${role.toLowerCase()}`}>{role}</span>;
};

export default RoleBadge;
