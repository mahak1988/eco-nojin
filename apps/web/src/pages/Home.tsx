import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

const Home: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div style={{ padding: '2rem' }}>
      <h2>به Eco Nojin خوش آمدید</h2>
      <p>پلتفرم جامع محیط‌زیست با همزاد دیجیتال <strong>HydroMa Nojin</strong></p>
      <p>مدل‌سازی، تحلیل، پایش و احیای اکوسیستم‌ها با قدرت هوش مصنوعی و شبیه‌سازهای علمی.</p>
      {!isAuthenticated && (
        <Link to="/login">برای شروع وارد شوید</Link>
      )}
    </div>
  );
};

export default Home;
