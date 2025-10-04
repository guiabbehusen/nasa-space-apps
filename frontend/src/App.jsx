// src/App.jsx
import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Corrigir ícones do Leaflet
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

export default function App() {
  const [position, setPosition] = useState(null);
  const [time, setTime] = useState(new Date());

  // Atualiza geolocalização
  useEffect(() => {
    if (navigator.geolocation) {
      const watcher = navigator.geolocation.watchPosition(
        (pos) => {
          setPosition([pos.coords.latitude, pos.coords.longitude]);
        },
        (err) => console.error(err),
        { enableHighAccuracy: true }
      );
      return () => navigator.geolocation.clearWatch(watcher);
    }
  }, []);

  // Atualiza horário a cada segundo
  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-blue-900 text-white p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">AirGuardian 🌍</h1>
        <nav className="hidden md:flex gap-4">
          <a href="#">Mapa</a>
          <a href="#">Dados</a>
          <a href="#">Sobre</a>
        </nav>
      </header>

      {/* Conteúdo */}
      <main className="flex-1 flex">
        {/* Mapa */}
        <div className="flex-1">
          {position ? (
            <MapContainer
              center={position}
              zoom={13}
              className="h-full w-full"
            >
              <TileLayer
                attribution="&copy; OpenStreetMap"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={position}>
                <Popup>Você está aqui 📍</Popup>
              </Marker>
            </MapContainer>
          ) : (
            <p className="text-center mt-10">Carregando localização...</p>
          )}
        </div>

        {/* Painel lateral (desktop) */}
        <aside className="hidden md:block w-80 bg-gray-100 p-4 border-l">
          <h2 className="font-bold text-lg mb-2">Dados em tempo real</h2>
          {position ? (
            <ul>
              <li>Latitude: {position[0].toFixed(6)}</li>
              <li>Longitude: {position[1].toFixed(6)}</li>
              <li>Última atualização: {time.toLocaleTimeString()}</li>
            </ul>
          ) : (
            <p>Aguardando localização...</p>
          )}
        </aside>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white p-2 text-center text-sm">
        Powered by NASA Space Apps + APIs
      </footer>
    </div>
  );
}

