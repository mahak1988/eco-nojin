-- Insert demo tenant
INSERT INTO public.tenants (id, name, slug) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'Acme Corporation', 'acme');

-- Insert demo projects
INSERT INTO public.projects (id, tenant_id, name, description, status) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 
     'Website Redesign', 'Redesign company website', 'active'),
    ('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', 
     'Mobile App', 'Develop mobile application', 'active');