export type ThemeName = 'Modern' | 'Minimal' | 'Classic';

export interface BrandingTheme {
  logoUrl: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  themeName: ThemeName;
}

export interface CustomDomain {
  domain: string;
  status: 'Unverified' | 'Pending' | 'Verified';
  lastUpdated: string;
}

export type ClientStatus = 'Active' | 'Invited' | 'Inactive';
export type ClientRole = 'Owner' | 'Admin' | 'Editor' | 'Viewer';

export interface ClientRecord {
  id: string;
  name: string;
  email: string;
  role: ClientRole;
  status: ClientStatus;
  workspaces: string[];
  invitedAt: string;
  lastActive: string;
}

export interface WorkspaceMetrics {
  activeClients: number;
  activeProjects: number;
  utilizationRate: number;
  satisfactionScore: number;
  revenue: number;
  lastUpdated: string;
}

export interface WorkspaceRecord {
  id: string;
  name: string;
  industry: string;
  metrics: WorkspaceMetrics;
}

export interface InvitePayload {
  name: string;
  email: string;
  role: ClientRole;
  workspaceId: string;
}

export interface BrandingUpdatePayload {
  logoUrl?: string;
  primaryColor?: string;
  secondaryColor?: string;
  accentColor?: string;
  themeName?: ThemeName;
}
