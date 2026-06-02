// frontend/src/components/ResultsDashboard.tsx
"use client"
import { useMemo } from "react"
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, 
  LineElement, BarElement, Title, Tooltip, Legend, ArcElement
} from "chart.js"
import { Line, Bar, Pie } from "react-chartjs-2"
import jsPDF from "jspdf"
import html2canvas from "html2canvas"

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement)

interface DashboardData {
  yield_kg_ha: number
  water_need_mm: number
  soc_change_t_ha: number
  recommendations: string[]
  historical?: Array<{ year: number; yield: number; water: number }>
}

export default function ResultsDashboard({ data }: { data: DashboardData }) {
  const chartData = useMemo(() => {
    const historical = data.historical || []
    return {
      yield: {
        labels: historical.map(h => h.year),
        datasets: [{
          label: "Yield (kg/ha)",
          data: historical.map(h => h.yield),
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.1)",
          tension: 0.4,
        }]
      },
      water: {
        labels: ["Current", "Regional Avg", "Optimal"],
        datasets: [{
          label: "Water Use (mm)",
          data: [data.water_need_mm, 420, 300],
          backgroundColor: ["#10b981", "#f59e0b", "#3b82f6"],
        }]
      },
      soc: {
        labels: ["Current SOC", "After 10yr"],
        datasets: [{
          data: [1.1, 1.1 + (data.soc_change_t_ha || 0)],
          backgroundColor: ["#6b7280", "#10b981"],
        }]
      }
    }
  }, [data])
  
  const exportPDF = async () => {
    const element = document.getElementById("dashboard-content")
    if (!element) return
    const canvas = await html2canvas(element)
    const imgData = canvas.toDataURL("image/png")
    const pdf = new jsPDF("p", "mm", "a4")
    pdf.addImage(imgData, "PNG", 10, 10, 190, 0)
    pdf.save("economugin-results.pdf")
  }
  
  return (
    <div id="dashboard-content" className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-gray-600">Predicted Yield</p>
          <p className="text-2xl font-bold text-green-700">{data.yield_kg_ha.toLocaleString()} kg/ha</p>
        </div>
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-gray-600">Water Need</p>
          <p className="text-2xl font-bold text-blue-700">{data.water_need_mm} mm</p>
        </div>
        <div className="p-4 bg-purple-50 rounded-lg">
          <p className="text-sm text-gray-600">SOC Change (10yr)</p>
          <p className="text-2xl font-bold text-purple-700">+{data.soc_change_t_ha} t/ha</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-4 border rounded">
          <h3 className="font-semibold mb-4">Yield Trend</h3>
          {charts.Line ? (
            <charts.Line
              data={chartData.yield}
              options={{
                responsive: true,
                plugins: { legend: { display: false } },
              }}
            />
          ) : (
            <div className="text-sm text-gray-500">Charts not available.</div>
          )}
        </div>
        <div className="p-4 border rounded">
          <h3 className="font-semibold mb-4">Water Comparison</h3>
          {charts.Bar ? (
            <charts.Bar
              data={chartData.water}
              options={{
                responsive: true,
                plugins: { legend: { display: false } },
              }}
            />
          ) : (
            <div className="text-sm text-gray-500">Charts not available.</div>
          )}
        </div>
      </div>
      
      {data.recommendations?.length > 0 && (
        <div className="p-4 bg-yellow-50 rounded-lg">
          <h3 className="font-semibold mb-2">💡 Recommendations</h3>
          <ul className="list-disc ml-5 space-y-1">
            {data.recommendations.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </div>
      )}
      
      <button onClick={exportPDF} className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-700">
        📥 Export PDF
      </button>
    </div>
  )
}
