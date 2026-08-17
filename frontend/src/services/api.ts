const API_BASE = '/api/v1';

export class ApiService {
  private static getToken(): string | null {
    return localStorage.getItem('revenueos_token');
  }

  public static setToken(token: string) {
    localStorage.setItem('revenueos_token', token);
  }

  public static removeToken() {
    localStorage.removeItem('revenueos_token');
  }

  private static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      headers['X-Auth-Token'] = token;
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    const res = await fetch(`${API_BASE}${endpoint}`, config);
    if (res.status === 401) {
      this.removeToken();
    }

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      const msg = errData?.error?.message || errData?.detail || `HTTP Error ${res.status}`;
      throw new Error(msg);
    }

    if (res.status === 204) {
      return {} as T;
    }

    return res.json();
  }

  // Auth
  public static async login(email: string, password: string): Promise<any> {
    const data = await this.request<any>('/auth/login', {

      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (data?.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  }

  public static async getMe(): Promise<any> {
    return this.request<any>('/auth/me');
  }

  // Leads
  public static async getLeads(statusFilter?: string, search?: string): Promise<any[]> {
    let url = '/leads';
    const params = new URLSearchParams();
    if (statusFilter) params.append('status', statusFilter);
    if (search) params.append('search', search);
    if (params.toString()) url += `?${params.toString()}`;
    return this.request<any[]>(url);
  }

  public static async createLead(leadData: any): Promise<any> {
    return this.request<any>('/leads', {
      method: 'POST',
      body: JSON.stringify(leadData),
    });
  }

  public static async rescoreLead(leadId: string): Promise<any> {
    return this.request<any>(`/leads/${leadId}/rescore`, {
      method: 'POST',
    });
  }

  // Deals
  public static async getDeals(): Promise<any[]> {
    return this.request<any[]>('/deals');
  }

  public static async createDeal(dealData: any): Promise<any> {
    return this.request<any>('/deals', {
      method: 'POST',
      body: JSON.stringify(dealData),
    });
  }

  public static async updateDeal(dealId: string, dealData: any): Promise<any> {
    return this.request<any>(`/deals/${dealId}`, {
      method: 'PUT',
      body: JSON.stringify(dealData),
    });
  }

  public static async getDealForecast(): Promise<any> {
    return this.request<any>('/deals/forecast/summary');
  }

  // Customers
  public static async getCustomers(): Promise<any[]> {
    return this.request<any[]>('/customers');
  }

  public static async getCustomer360(id: string): Promise<any> {
    return this.request<any>(`/customers/${id}/360`);
  }

  // Tickets
  public static async getTickets(statusFilter?: string): Promise<any[]> {
    const url = statusFilter ? `/tickets?status_filter=${statusFilter}` : '/tickets';
    return this.request<any[]>(url);
  }

  public static async createTicket(ticketData: any): Promise<any> {
    return this.request<any>('/tickets', {
      method: 'POST',
      body: JSON.stringify(ticketData),
    });
  }

  public static async updateTicketStatus(id: string, status: string): Promise<any> {
    return this.request<any>(`/tickets/${id}/status?new_status=${status}`, {
      method: 'PUT',
    });
  }

  // Knowledge & RAG
  public static async getDocuments(): Promise<any[]> {
    return this.request<any[]>('/knowledge/documents');
  }

  public static async createDocument(title: string, content: string): Promise<any> {
    return this.request<any>('/knowledge/documents', {
      method: 'POST',
      body: JSON.stringify({ title, content, file_type: 'txt' }),
    });
  }

  public static async queryKnowledgeBase(question: string): Promise<any> {
    return this.request<any>('/knowledge/query', {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  }

  // AI Copilot & Executive Insights
  public static async queryCopilot(prompt: string): Promise<any> {
    return this.request<any>('/ai/copilot', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  public static async getExecutiveInsights(): Promise<any> {
    return this.request<any>('/ai/executive-insights');
  }

  // Workflows
  public static async getWorkflows(): Promise<any[]> {
    return this.request<any[]>('/workflows');
  }

  // Integrations
  public static async getIntegrations(): Promise<any[]> {
    return this.request<any[]>('/integrations');
  }

  // Billing
  public static async getBillingUsage(): Promise<any> {
    return this.request<any>('/billing/usage');
  }

  // Audit Logs
  public static async getAuditLogs(): Promise<any[]> {
    return this.request<any[]>('/audit-logs');
  }
}
