import { useState } from 'react'
import { Plus, Edit2, Trash2, Shield, Check, X } from 'lucide-react'
import Header from '../components/Header'

const roles = [
  { id: 1, name: 'Super Admin', users: 2, color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
  { id: 2, name: 'Agriculture Department', users: 8, color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' },
  { id: 3, name: 'District Officer', users: 15, color: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400' },
  { id: 4, name: 'Village Officer', users: 48, color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' },
  { id: 5, name: 'Farmer Group Leader', users: 96, color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' },
  { id: 6, name: 'Farmer', users: 4613, color: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400' },
]

const permissions = [
  { module: 'Dashboard', superAdmin: true, agriDept: true, districtOfficer: true, villageOfficer: true, groupLeader: true, farmer: true },
  { module: 'Land Registry', superAdmin: true, agriDept: true, districtOfficer: true, villageOfficer: true, groupLeader: false, farmer: false },
  { module: 'Farmers', superAdmin: true, agriDept: true, districtOfficer: true, villageOfficer: true, groupLeader: false, farmer: false },
  { module: 'Planting Seasons', superAdmin: true, agriDept: true, districtOfficer: true, villageOfficer: true, groupLeader: true, farmer: false },
  { module: 'Harvest Monitoring', superAdmin: true, agriDept: true, districtOfficer: true, villageOfficer: true, groupLeader: true, farmer: false },
  { module: 'Fertilizer Mgmt', superAdmin: true, agriDept: true, districtOfficer: true, villageOfficer: false, groupLeader: false, farmer: false },
  { module: 'Water & Irrigation', superAdmin: true, agriDept: true, districtOfficer: true, villageOfficer: false, groupLeader: false, farmer: false },
  { module: 'Production Analytics', superAdmin: true, agriDept: true, districtOfficer: true, villageOfficer: false, groupLeader: false, farmer: false },
  { module: 'GIS Explorer', superAdmin: true, agriDept: true, districtOfficer: false, villageOfficer: false, groupLeader: false, farmer: false },
  { module: 'AI Insights', superAdmin: true, agriDept: true, districtOfficer: true, villageOfficer: false, groupLeader: false, farmer: false },
  { module: 'Reports', superAdmin: true, agriDept: true, districtOfficer: true, villageOfficer: true, groupLeader: false, farmer: false },
  { module: 'Administration', superAdmin: true, agriDept: false, districtOfficer: false, villageOfficer: false, groupLeader: false, farmer: false },
]

const users = [
  { name: 'Ahmad Fauzi', email: 'ahmad.fauzi@indramayu.go.id', role: 'Super Admin', status: 'Active', last: '2 min ago' },
  { name: 'Dewi Sartika', email: 'dewi.sartika@pertanian.go.id', role: 'Agriculture Department', status: 'Active', last: '1 hour ago' },
  { name: 'Budi Prawoto', email: 'budi@karangampel.desa.id', role: 'Village Officer', status: 'Active', last: '3 hours ago' },
  { name: 'Rina Marlina', email: 'rina@leles.desa.id', role: 'Village Officer', status: 'Active', last: '1 day ago' },
  { name: 'Joko Susilo', email: 'joko.susilo@indramayu.go.id', role: 'District Officer', status: 'Inactive', last: '5 days ago' },
]

export default function Administration() {
  const [tab, setTab] = useState<'users' | 'roles' | 'permissions'>('users')

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Header title="Administration" subtitle="Manage users, roles, and permissions" />
      <div className="flex-1 overflow-y-auto p-6 space-y-6">

        {/* Tabs */}
        <div className="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-xl p-1 w-fit">
          {(['users', 'roles', 'permissions'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors capitalize ${tab === t ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}`}>
              {t}
            </button>
          ))}
        </div>

        {tab === 'users' && (
          <div className="card overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">User Management</h3>
              <button className="btn-primary flex items-center gap-1.5"><Plus className="w-3.5 h-3.5" /> Add User</button>
            </div>
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800">
                  {['Name', 'Email', 'Role', 'Status', 'Last Active', 'Action'].map(h => (
                    <th key={h} className="text-left text-xs font-semibold text-gray-500 dark:text-gray-400 px-5 py-3 uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.email} className="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50/50 dark:hover:bg-gray-800/30">
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-xs font-semibold text-green-700 dark:text-green-400">
                          {u.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                        </div>
                        <span className="text-sm font-medium text-gray-800 dark:text-gray-200">{u.name}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400">{u.email}</td>
                    <td className="px-5 py-3"><span className="badge badge-blue">{u.role}</span></td>
                    <td className="px-5 py-3"><span className={`badge ${u.status === 'Active' ? 'badge-green' : 'badge-gray'}`}>{u.status}</span></td>
                    <td className="px-5 py-3 text-xs text-gray-400">{u.last}</td>
                    <td className="px-5 py-3">
                      <div className="flex gap-1">
                        <button className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"><Edit2 className="w-3.5 h-3.5" /></button>
                        <button className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-500 hover:text-red-500"><Trash2 className="w-3.5 h-3.5" /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'roles' && (
          <div className="grid grid-cols-3 gap-4">
            {roles.map(r => (
              <div key={r.id} className="card p-5">
                <div className="flex items-start justify-between">
                  <div className="w-10 h-10 rounded-xl bg-green-50 dark:bg-green-900/20 flex items-center justify-center">
                    <Shield className="w-5 h-5 text-green-700 dark:text-green-400" />
                  </div>
                  <div className="flex gap-1">
                    <button className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"><Edit2 className="w-3.5 h-3.5" /></button>
                  </div>
                </div>
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mt-3">{r.name}</h3>
                <p className="text-xs text-gray-400 mt-1">{r.users.toLocaleString()} users</p>
                <span className={`badge mt-2 ${r.color}`}>{r.name}</span>
              </div>
            ))}
          </div>
        )}

        {tab === 'permissions' && (
          <div className="card overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Permissions Matrix</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/30">
                    <th className="text-left text-xs font-semibold text-gray-500 dark:text-gray-400 px-5 py-3 uppercase tracking-wide">Module</th>
                    {['Super Admin', 'Agri Dept', 'District', 'Village', 'Group Leader', 'Farmer'].map(r => (
                      <th key={r} className="text-center text-xs font-semibold text-gray-500 dark:text-gray-400 px-4 py-3 uppercase tracking-wide">{r}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {permissions.map(p => (
                    <tr key={p.module} className="border-b border-gray-50 dark:border-gray-800/50">
                      <td className="px-5 py-3 text-sm font-medium text-gray-700 dark:text-gray-300">{p.module}</td>
                      {[p.superAdmin, p.agriDept, p.districtOfficer, p.villageOfficer, p.groupLeader, p.farmer].map((v, i) => (
                        <td key={i} className="px-4 py-3 text-center">
                          {v
                            ? <Check className="w-4 h-4 text-green-600 dark:text-green-400 mx-auto" />
                            : <X className="w-4 h-4 text-gray-300 dark:text-gray-700 mx-auto" />
                          }
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
