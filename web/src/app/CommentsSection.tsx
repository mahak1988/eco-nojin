'use client';

import { useState } from 'react';
import { MessageSquare, Send, User, ThumbsUp, Reply } from 'lucide-react';
import { useComments } from '@/lib/supabase/hooks';
import StarRating from './StarRating';
import { formatDistanceToNow } from 'date-fns';
import { faIR } from 'date-fns/locale';

interface CommentsSectionProps {
  resourceId: string;
}

export default function CommentsSection({ resourceId }: CommentsSectionProps) {
  const { comments, loading, addComment } = useComments(resourceId);
  const [newComment, setNewComment] = useState('');
  const [newRating, setNewRating] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setSubmitting(true);
    const result = await addComment(newComment, newRating);
    if (result) {
      setNewComment('');
      setNewRating(0);
    }
    setSubmitting(false);
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <MessageSquare className="w-6 h-6 text-green-600" />
        <h2 className="text-2xl font-bold">نظرات و نقدها</h2>
        <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-sm font-medium">
          {comments.length}
        </span>
      </div>

      {/* Comment Form */}
      <form onSubmit={handleSubmit} className="mb-8 bg-gray-50 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-sm font-medium">امتیاز شما:</span>
          <StarRating rating={newRating} onRate={setNewRating} />
        </div>
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="نظر خود را بنویسید..."
          className="w-full px-4 py-3 border-2 rounded-lg focus:border-green-500 focus:outline-none resize-none mb-3"
          rows={3}
        />
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={submitting || !newComment.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            ارسال نظر
          </button>
        </div>
      </form>

      {/* Comments List */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">در حال بارگذاری...</div>
      ) : comments.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-30" />
          <p>هنوز نظری ثبت نشده. اولین نفر باشید!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.id} className="border-r-4 border-green-500 pr-4 py-2">
              <div className="flex items-start gap-3 mb-2">
                {comment.user_avatar ? (
                  <img src={comment.user_avatar} alt="" className="w-10 h-10 rounded-full" />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-white font-bold">
                    {comment.user_name.charAt(0)}
                  </div>
                )}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold">{comment.user_name}</span>
                    {comment.rating && <StarRating rating={comment.rating} size="sm" readonly />}
                  </div>
                  <p className="text-gray-700 mb-2">{comment.content}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>
                      {formatDistanceToNow(new Date(comment.created_at), { 
                        addSuffix: true, 
                        locale: faIR 
                      })}
                    </span>
                    <button className="flex items-center gap-1 hover:text-green-600 transition">
                      <ThumbsUp className="w-4 h-4" />
                      {comment.likes_count}
                    </button>
                    <button className="flex items-center gap-1 hover:text-green-600 transition">
                      <Reply className="w-4 h-4" />
                      پاسخ
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}