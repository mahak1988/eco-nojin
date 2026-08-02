Add to App.tsx lazy imports and routes:

const EoHubPage = lazy(() => import("./pages/EoHubPage"));

<Route path="eo" element={<EoHubPage />} />
<Route path="satellite/eo" element={<EoHubPage />} />
