import { useNavigate, useLocation } from "react-router-dom";
import { LoginForm } from "../features/auth/LoginForm";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from || "/dashboard";

  return (
    <div className="flex min-h-[70vh] items-center justify-center p-6">
      <LoginForm onSuccess={() => navigate(from, { replace: true })} />
    </div>
  );
}
