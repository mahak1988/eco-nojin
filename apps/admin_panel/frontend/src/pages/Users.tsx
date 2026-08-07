import { useState, useEffect } from 'react'
import {
  Search, Shield, ShieldOff, CheckCircle2, XCircle, Trash2,
  Loader2, AlertCircle, RefreshCw,
} from 'lucide-react'
import { fetchUsers, updateUserStatus, updateUserRole, deleteUser, AdminUser } from '../api/adminApi'
import { useToast } from '../components/Toast'

export default function Users() {
  const { toast } = useToast()
  const [users, setUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null)

  const loadUsers = () => {
    setLoading(true)
    setError(null)
    const params: Record<string, unknown> = { limit: 200 }
    if (search) params.search = search
    if (roleFilter) params.role = roleFilter
    if (statusFilter === 'active') params.is_active = true
    if (statusFilter === 'inactive') params.is_active = false
    if (statusFilter === 'superuser') params.is_superuser = true

    fetchUsers(params as any)
      .then(setUsers)
      .catch((err) => setError(err?.message || 'خطا در بارگذاری کاربران'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadUsers()
  }, [roleFilter, statusFilter])

  const handleSearch = () => loadUsers()

  const handleToggleStatus = async (user: AdminUser) => {
    setActionLoading(user.id)
    try {
      const updated = await updateUserStatus(user.id, !user.is_active)
      setUsers(users.map((u) => (u.id === updated.id ? updated : u)))
      toast(user.is_active ? 'کاربر غیرفعال شد' : 'کاربر فعال شد', 'success')
    } catch (err: any) {
      toast(err?.response?.data?.detail || 'خطا در تغییر وضعیت', 'error')
    } finally {
      setActionLoading(null)
    }
  }

  const handleToggleRole = async (user: AdminUser) => {
    setActionLoading(user.id)
    try {
      const updated = await updateUserRole(user.id, !user.is_superuser)
      setUsers(users.map((u) => (u.id === updated.id ? updated : u)))
      toast(user.is_superuser ? 'دسترسی سوپریوزر برداشته شد' : 'کاربر سوپریوزر شد', 'success')
    } catch (err: any) {
      toast(err?.response?.data?.detail || 'خطا در تغییر نقش', 'error')
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async (userId: number) => {
    setActionLoading(userId)
    try {
      await deleteUser(userId)
      setUsers(users.filter((u) => u.id !== userId))
      setConfirmDelete(null)
      toast('کاربر حذف شد', 'success')
    } catch (err: any) {
      toast(err?.response?.data?.detail || 'خطا در حذف کاربر', 'error')
    } finally {
      setActionLoading(null)
    }
  }

  const filtered = search
    ? users.filter(
        (u) =>
          u.email.toLowerCase().includes(search.toLowerCase()) ||
          (u.full_name || '').toLowerCase().includes(search.toLowerCase())
      )
    : users

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">کاربران</h1>
          <p className="text-muted-foreground">مدیریت کاربران سیستم · {users.length} نفر</p>
        </div>
        <button
          onClick={loadUsers}
          className="flex items-center gap-2 px-3 py-2 border rounded-lg hover:bg-accent text-sm"
        >
          <RefreshCw className="w-4 h-4" /> به‌روزرسانی
        </button>
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="جستجو با نام یا ایمیل..."
            className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm"
          />
        </div>
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg text-sm"
        >
          <option value="">همه نقش‌ها</option>
          <option value="admin">مدیر</option>
          <option value="farmer">کشاورز</option>
          <option value="manager">مدیر مزرعه</option>
          <option value="viewer">مشاهده‌گر</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg text-sm"
        >
          <option value="">همه وضعیت‌ها</option>
          <option value="active">فعال</option>
          <option value="inactive">غیرفعال</option>
          <option value="superuser">سوپریوزر</option>
        </select>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-eco-600" />
        </div>
      )}

      {!loading && (
        <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="text-right p-4">شناسه</th>
                  <th className="text-right p-4">نام</th>
                  <th className="text-right p-4">ایمیل</th>
                  <th className="text-right p-4">نقش</th>
                  <th className="text-right p-4">وضعیت</th>
                  <th className="text-right p-4">سوپریوزر</th>
                  <th className="text-right p-4">عملیات</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="p-8 text-center text-muted-foreground">
                      کاربری یافت نشد
                    </td>
                  </tr>
                ) : (
                  filtered.map((user) => (
                    <tr key={user.id} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="p-4 font-mono text-xs">{user.id}</td>
                      <td className="p-4 font-medium">{user.full_name || '—'}</td>
                      <td className="p-4 text-muted-foreground">{user.email}</td>
                      <td className="p-4">
                        <span className="px-2 py-1 rounded-full bg-eco-100 text-eco-800 text-xs">
                          {user.role}
                        </span>
                      </td>
                      <td className="p-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
                            user.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {user.is_active ? (
                            <CheckCircle2 className="w-3 h-3" />
                          ) : (
                            <XCircle className="w-3 h-3" />
                          )}
                          {user.is_active ? 'فعال' : 'غیرفعال'}
                        </span>
                      </td>
                      <td className="p-4">
                        {user.is_superuser ? (
                          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800">
                            <Shield className="w-3 h-3" /> بله
                          </span>
                        ) : (
                          <span className="text-muted-foreground text-xs">—</span>
                        )}
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleToggleStatus(user)}
                            disabled={actionLoading === user.id}
                            className="p-1.5 hover:bg-accent rounded-lg text-xs disabled:opacity-50"
                            title={user.is_active ? 'غیرفعال کردن' : 'فعال کردن'}
                          >
                            {user.is_active ? (
                              <XCircle className="w-4 h-4 text-amber-600" />
                            ) : (
                              <CheckCircle2 className="w-4 h-4 text-green-600" />
                            )}
                          </button>
                          <button
                            onClick={() => handleToggleRole(user)}
                            disabled={actionLoading === user.id}
                            className="p-1.5 hover:bg-accent rounded-lg text-xs disabled:opacity-50"
                            title={user.is_superuser ? 'حذف سوپریوزر' : 'اعطای سوپریوزر'}
                          >
                            {user.is_superuser ? (
                              <ShieldOff className="w-4 h-4 text-purple-600" />
                            ) : (
                              <Shield className="w-4 h-4 text-purple-600" />
                            )}
                          </button>
                          {confirmDelete === user.id ? (
                            <div className="flex items-center gap-1">
                              <button
                                onClick={() => handleDelete(user.id)}
                                className="p-1.5 bg-red-100 text-red-700 rounded-lg text-xs font-medium"
                              >
                                تأیید
                              </button>
                              <button
                                onClick={() => setConfirmDelete(null)}
                                className="p-1.5 hover:bg-accent rounded-lg text-xs"
                              >
                                انصراف
                              </button>
                            </div>
                          ) : (
                            <button
                              onClick={() => setConfirmDelete(user.id)}
                              disabled={actionLoading === user.id}
                              className="p-1.5 hover:bg-accent rounded-lg disabled:opacity-50"
                              title="حذف کاربر"
                            >
                              <Trash2 className="w-4 h-4 text-red-500" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
