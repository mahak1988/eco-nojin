-- Econojin Library - Additional Tables Migration
-- Run this in Supabase SQL Editor

-- Enable UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================================================
-- RESOURCES TABLE (Enhanced)
-- ========================================================================

CREATE TABLE IF NOT EXISTS resources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  resource_type TEXT NOT NULL CHECK (resource_type IN ('book', 'article', 'thesis', 'video', 'podcast', 'dataset')),
  file_url TEXT NOT NULL,
  category TEXT NOT NULL,
  language TEXT DEFAULT 'fa',
  author TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  download_count INTEGER DEFAULT 0,
  view_count INTEGER DEFAULT 0,
  rating DECIMAL(3,2) DEFAULT 0,
  rating_count INTEGER DEFAULT 0,
  cover_color TEXT DEFAULT 'from-green-400 to-emerald-600',
  uploader_id UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_resources_category ON resources(category);
CREATE INDEX IF NOT EXISTS idx_resources_tags ON resources USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_resources_created ON resources(created_at DESC);

-- ========================================================================
-- COMMENTS TABLE
-- ========================================================================

CREATE TABLE IF NOT EXISTS comments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  user_name TEXT NOT NULL,
  user_avatar TEXT,
  content TEXT NOT NULL,
  rating DECIMAL(3,2),
  parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
  likes_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comments_resource ON comments(resource_id);
CREATE INDEX IF NOT EXISTS idx_comments_user ON comments(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_created ON comments(created_at DESC);

-- ========================================================================
-- WISHLISTS TABLE
-- ========================================================================

CREATE TABLE IF NOT EXISTS wishlists (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, resource_id)
);

CREATE INDEX IF NOT EXISTS idx_wishlists_user ON wishlists(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlists_resource ON wishlists(resource_id);

-- ========================================================================
-- STORAGE BUCKET
-- ========================================================================

-- Create storage bucket for resources (run in Supabase Storage UI or SQL)
-- Note: This requires Supabase Storage to be enabled
-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('resources', 'resources', true);

-- ========================================================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================================================

-- Enable RLS
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE wishlists ENABLE ROW LEVEL SECURITY;

-- Resources policies
CREATE POLICY "Resources are viewable by everyone" 
  ON resources FOR SELECT USING (true);

CREATE POLICY "Authenticated users can insert resources" 
  ON resources FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- Comments policies
CREATE POLICY "Comments are viewable by everyone" 
  ON comments FOR SELECT USING (true);

CREATE POLICY "Authenticated users can insert comments" 
  ON comments FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own comments" 
  ON comments FOR DELETE USING (auth.uid() = user_id);

-- Wishlists policies
CREATE POLICY "Users can view their own wishlist" 
  ON wishlists FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert to their own wishlist" 
  ON wishlists FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete from their own wishlist" 
  ON wishlists FOR DELETE USING (auth.uid() = user_id);

-- ========================================================================
-- FUNCTIONS
-- ========================================================================

-- Function to increment download count
CREATE OR REPLACE FUNCTION increment_download(resource_uuid UUID)
RETURNS VOID AS $$
BEGIN
  UPDATE resources 
  SET download_count = download_count + 1 
  WHERE id = resource_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to increment view count
CREATE OR REPLACE FUNCTION increment_view(resource_uuid UUID)
RETURNS VOID AS $$
BEGIN
  UPDATE resources 
  SET view_count = view_count + 1 
  WHERE id = resource_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update resource rating
CREATE OR REPLACE FUNCTION update_resource_rating(resource_uuid UUID)
RETURNS VOID AS $$
BEGIN
  UPDATE resources 
  SET 
    rating = (
      SELECT COALESCE(AVG(rating), 0) 
      FROM comments 
      WHERE resource_id = resource_uuid AND rating IS NOT NULL
    ),
    rating_count = (
      SELECT COUNT(*) 
      FROM comments 
      WHERE resource_id = resource_uuid AND rating IS NOT NULL
    )
  WHERE id = resource_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to auto-update rating when comment is added
CREATE OR REPLACE FUNCTION trigger_update_rating()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM update_resource_rating(NEW.resource_id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_rating_on_comment
AFTER INSERT OR UPDATE OR DELETE ON comments
FOR EACH ROW EXECUTE FUNCTION trigger_update_rating();

-- ========================================================================
-- SEED DATA
-- ========================================================================

INSERT INTO resources (title, description, resource_type, file_url, category, language, author, tags, cover_color, download_count, view_count, rating, rating_count) VALUES
('مقدمه‌ای بر تغییرات اقلیمی', 'کتاب جامع درباره علل و اثرات تغییرات اقلیمی و راه‌حل‌های علمی', 'book', 'https://example.com/climate.pdf', 'environmental_science', 'fa', 'دکتر محمد رضایی', ARRAY['climate', 'environment', 'science'], 'from-green-400 to-emerald-600', 1250, 8540, 4.8, 234),
('Blockchain for Sustainability', 'Research paper on blockchain applications in environmental sustainability', 'article', 'https://example.com/blockchain.pdf', 'blockchain', 'en', 'Dr. Sarah Chen', ARRAY['blockchain', 'sustainability', 'web3'], 'from-blue-400 to-cyan-600', 890, 5620, 4.6, 156),
('کشاورزی پایدار در ایران', 'بررسی تکنیک‌های نوین کشاورزی پایدار و حفظ خاک', 'thesis', 'https://example.com/agriculture.pdf', 'agriculture', 'fa', 'مهندس علی کریمی', ARRAY['agriculture', 'sustainability', 'iran'], 'from-yellow-400 to-orange-600', 540, 3210, 4.9, 89),
('کاربرد هوش مصنوعی در محیط زیست', 'ویدیو آموزشی درباره کاربردهای AI در حفاظت از محیط زیست', 'video', 'https://example.com/ai-env.mp4', 'ai', 'fa', 'دکتر ماریا گارسیا', ARRAY['ai', 'machine-learning', 'environment'], 'from-purple-400 to-pink-600', 2340, 15670, 4.7, 445),
('اقتصاد کربن و بازارهای آینده', 'تحلیل بازارهای اعتبار کربن و فرصت‌های سرمایه‌گذاری', 'article', 'https://example.com/carbon-econ.pdf', 'economics', 'fa', 'دکتر رضا کریمی', ARRAY['economics', 'carbon', 'markets'], 'from-emerald-400 to-teal-600', 1560, 9870, 4.5, 278),
('پادکست: آینده انرژی‌های تجدیدپذیر', 'گفتگو با متخصصان درباره آینده انرژی‌های پاک', 'podcast', 'https://example.com/energy-podcast.mp3', 'energy', 'fa', 'تیم اکونوژین', ARRAY['podcast', 'energy', 'renewable'], 'from-red-400 to-rose-600', 3420, 18920, 4.8, 612)
ON CONFLICT DO NOTHING;