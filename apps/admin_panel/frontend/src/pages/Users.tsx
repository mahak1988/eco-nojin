import { useTranslation } from 'react-i18next'

export default function Users() {
  const { t } = useTranslation()

  const users = [
    { id: 1, name: 'علی محمدی', email: 'ali@example.com', role: 'admin', status: 'active' },
    { id: 2, name: 'سارا احمدی', email: 'sara@example.com', role: 'user', status: 'active' },
    { id: 3, name: 'رضا کریمی', email: 'reza@example.com', role: 'user', status: 'inactive' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Users</h1>
        <p className="text-muted-foreground">Manage system users</p>
      </div>

      <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-right p-4">Name</th>
              <th className="text-right p-4">Email</th>
              <th className="text-right p-4">Role</th>
              <th className="text-right p-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b last:border-0 hover:bg-muted/50">
                <td className="p-4">{user.name}</td>
                <td className="p-4 text-muted-foreground">{user.email}</td>
                <td className="p-4">
                  <span className="px-2 py-1 rounded-full bg-eco-100 text-eco-800 text-xs">
                    {user.role}
                  </span>
                </td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    user.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {user.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}