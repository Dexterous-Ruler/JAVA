import React, { createContext, useEffect, useMemo, useState } from 'react';
import {
  BrandingTheme,
  BrandingUpdatePayload,
  ClientRecord,
  ClientRole,
  CustomDomain,
  InvitePayload,
  WorkspaceRecord
} from '../types';

interface AggregatedMetrics {
  totalActiveClients: number;
  totalActiveProjects: number;
  totalRevenue: number;
  averageUtilizationRate: number;
  averageSatisfactionScore: number;
}

interface AgencyContextValue {
  branding: BrandingTheme;
  customDomain: CustomDomain;
  clients: ClientRecord[];
  workspaces: WorkspaceRecord[];
  currentWorkspaceId: string;
  roles: ClientRole[];
  aggregatedMetrics: AggregatedMetrics;
  updateBranding: (payload: BrandingUpdatePayload) => void;
  setCustomDomain: (domain: string) => void;
  inviteClient: (payload: InvitePayload) => void;
  assignClientRole: (clientId: string, role: ClientRole) => void;
  switchWorkspace: (workspaceId: string) => void;
}

const BASE_BRANDING: BrandingTheme = {
  logoUrl: 'https://dummyimage.com/120x40/1f3c88/ffffff&text=Agency',
  primaryColor: '#1f3c88',
  secondaryColor: '#4e6ef2',
  accentColor: '#f97316',
  themeName: 'Modern'
};

const DEFAULT_DOMAIN: CustomDomain = {
  domain: 'agency.example.com',
  status: 'Verified',
  lastUpdated: '2024-10-01T08:30:00Z'
};

const DEFAULT_ROLES: ClientRole[] = ['Owner', 'Admin', 'Editor', 'Viewer'];

const DEFAULT_WORKSPACES: WorkspaceRecord[] = [
  {
    id: 'workspace-growth',
    name: 'Growth Labs',
    industry: 'SaaS',
    metrics: {
      activeClients: 18,
      activeProjects: 32,
      utilizationRate: 0.78,
      satisfactionScore: 4.6,
      revenue: 88000,
      lastUpdated: '2024-10-15T14:12:00Z'
    }
  },
  {
    id: 'workspace-retail',
    name: 'Retail Collective',
    industry: 'Retail',
    metrics: {
      activeClients: 12,
      activeProjects: 21,
      utilizationRate: 0.71,
      satisfactionScore: 4.3,
      revenue: 62000,
      lastUpdated: '2024-10-15T12:47:00Z'
    }
  },
  {
    id: 'workspace-fintech',
    name: 'Fintech Alliance',
    industry: 'Finance',
    metrics: {
      activeClients: 9,
      activeProjects: 16,
      utilizationRate: 0.82,
      satisfactionScore: 4.8,
      revenue: 91000,
      lastUpdated: '2024-10-14T09:52:00Z'
    }
  }
];

const DEFAULT_CLIENTS: ClientRecord[] = [
  {
    id: 'client-1',
    name: 'Aurora Analytics',
    email: 'ops@aurora.io',
    role: 'Owner',
    status: 'Active',
    workspaces: ['workspace-growth', 'workspace-fintech'],
    invitedAt: '2024-09-01T10:00:00Z',
    lastActive: '2024-10-20T15:21:00Z'
  },
  {
    id: 'client-2',
    name: 'Northwind Stores',
    email: 'contact@northwind.com',
    role: 'Admin',
    status: 'Active',
    workspaces: ['workspace-retail'],
    invitedAt: '2024-09-10T14:30:00Z',
    lastActive: '2024-10-19T18:54:00Z'
  },
  {
    id: 'client-3',
    name: 'Ledger Labs',
    email: 'hello@ledgerlabs.io',
    role: 'Viewer',
    status: 'Invited',
    workspaces: ['workspace-fintech'],
    invitedAt: '2024-10-10T09:45:00Z',
    lastActive: '2024-10-10T09:45:00Z'
  }
];

interface AgencyState {
  branding: BrandingTheme;
  customDomain: CustomDomain;
  clients: ClientRecord[];
  workspaces: WorkspaceRecord[];
  currentWorkspaceId: string;
}

const computeAggregatedMetrics = (workspaces: WorkspaceRecord[]): AggregatedMetrics => {
  if (workspaces.length === 0) {
    return {
      totalActiveClients: 0,
      totalActiveProjects: 0,
      totalRevenue: 0,
      averageUtilizationRate: 0,
      averageSatisfactionScore: 0
    };
  }

  return workspaces.reduce(
    (acc, workspace, _, array) => {
      acc.totalActiveClients += workspace.metrics.activeClients;
      acc.totalActiveProjects += workspace.metrics.activeProjects;
      acc.totalRevenue += workspace.metrics.revenue;
      acc.averageUtilizationRate += workspace.metrics.utilizationRate / array.length;
      acc.averageSatisfactionScore += workspace.metrics.satisfactionScore / array.length;
      return acc;
    },
    {
      totalActiveClients: 0,
      totalActiveProjects: 0,
      totalRevenue: 0,
      averageUtilizationRate: 0,
      averageSatisfactionScore: 0
    }
  );
};

const updateThemeVariables = (branding: BrandingTheme) => {
  const root = document.documentElement;
  root.style.setProperty('--color-primary', branding.primaryColor);
  root.style.setProperty('--color-secondary', branding.secondaryColor);
  root.style.setProperty('--color-accent', branding.accentColor);
};

export const AgencyContext = createContext<AgencyContextValue | undefined>(undefined);

export const AgencyProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [state, setState] = useState<AgencyState>({
    branding: BASE_BRANDING,
    customDomain: DEFAULT_DOMAIN,
    clients: DEFAULT_CLIENTS,
    workspaces: DEFAULT_WORKSPACES,
    currentWorkspaceId: DEFAULT_WORKSPACES[0].id
  });

  useEffect(() => {
    updateThemeVariables(state.branding);
  }, [state.branding]);

  const contextValue = useMemo<AgencyContextValue>(() => {
    const updateBranding = (payload: BrandingUpdatePayload) => {
      setState((prev) => ({
        ...prev,
        branding: { ...prev.branding, ...payload }
      }));
    };

    const setCustomDomain = (domain: string) => {
      setState((prev) => ({
        ...prev,
        customDomain: {
          domain,
          status: domain ? 'Pending' : prev.customDomain.status,
          lastUpdated: new Date().toISOString()
        }
      }));
    };

    const inviteClient = ({ name, email, role, workspaceId }: InvitePayload) => {
      const timestamp = new Date().toISOString();
      setState((prev) => ({
        ...prev,
        clients: [
          ...prev.clients,
          {
            id: `client-${Date.now()}`,
            name,
            email,
            role,
            status: 'Invited',
            workspaces: [workspaceId],
            invitedAt: timestamp,
            lastActive: timestamp
          }
        ]
      }));
    };

    const assignClientRole = (clientId: string, role: ClientRole) => {
      setState((prev) => ({
        ...prev,
        clients: prev.clients.map((client) =>
          client.id === clientId
            ? {
                ...client,
                role,
                status: client.status === 'Invited' ? 'Active' : client.status
              }
            : client
        )
      }));
    };

    const switchWorkspace = (workspaceId: string) => {
      setState((prev) => ({
        ...prev,
        currentWorkspaceId: workspaceId
      }));
    };

    return {
      branding: state.branding,
      customDomain: state.customDomain,
      clients: state.clients,
      workspaces: state.workspaces,
      currentWorkspaceId: state.currentWorkspaceId,
      roles: DEFAULT_ROLES,
      aggregatedMetrics: computeAggregatedMetrics(state.workspaces),
      updateBranding,
      setCustomDomain,
      inviteClient,
      assignClientRole,
      switchWorkspace
    };
  }, [state]);

  return <AgencyContext.Provider value={contextValue}>{children}</AgencyContext.Provider>;
};
