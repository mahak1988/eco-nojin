-- Enable RLS on all tables
ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;

-- Helper function to get current user's tenant
CREATE OR REPLACE FUNCTION public.get_user_tenant()
RETURNS UUID AS $$
    SELECT tenant_id FROM public.profiles WHERE id = auth.uid();
$$ LANGUAGE sql SECURITY DEFINER;

-- Helper function to check user role
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
    SELECT role = 'admin' FROM public.profiles WHERE id = auth.uid();
$$ LANGUAGE sql SECURITY DEFINER;

-- Tenants policies
CREATE POLICY "Users can view their own tenant" ON public.tenants
    FOR SELECT USING (id = public.get_user_tenant());

CREATE POLICY "Admins can update their tenant" ON public.tenants
    FOR UPDATE USING (id = public.get_user_tenant() AND public.is_admin());

-- Profiles policies
CREATE POLICY "Users can view profiles in their tenant" ON public.profiles
    FOR SELECT USING (tenant_id = public.get_user_tenant());

CREATE POLICY "Users can update their own profile" ON public.profiles
    FOR UPDATE USING (id = auth.uid());

CREATE POLICY "Admins can manage all profiles in their tenant" ON public.profiles
    FOR ALL USING (tenant_id = public.get_user_tenant() AND public.is_admin());

-- Projects policies
CREATE POLICY "Users can view projects in their tenant" ON public.projects
    FOR SELECT USING (tenant_id = public.get_user_tenant());

CREATE POLICY "Users can create projects in their tenant" ON public.projects
    FOR INSERT WITH CHECK (tenant_id = public.get_user_tenant());

CREATE POLICY "Users can update projects in their tenant" ON public.projects
    FOR UPDATE USING (tenant_id = public.get_user_tenant());

CREATE POLICY "Users can delete projects in their tenant" ON public.projects
    FOR DELETE USING (tenant_id = public.get_user_tenant());

-- Tasks policies
CREATE POLICY "Users can view tasks in their tenant" ON public.tasks
    FOR SELECT USING (tenant_id = public.get_user_tenant());

CREATE POLICY "Users can create tasks in their tenant" ON public.tasks
    FOR INSERT WITH CHECK (tenant_id = public.get_user_tenant());

CREATE POLICY "Users can update tasks in their tenant" ON public.tasks
    FOR UPDATE USING (tenant_id = public.get_user_tenant());

CREATE POLICY "Users can delete tasks in their tenant" ON public.tasks
    FOR DELETE USING (tenant_id = public.get_user_tenant());

-- Realtime publication
ALTER PUBLICATION supabase_realtime ADD TABLE public.tasks;
ALTER PUBLICATION supabase_realtime ADD TABLE public.projects;