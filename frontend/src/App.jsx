import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function App() {
  const [position, setPosition] = useState(null);

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.watchPosition(
        (pos) => {
          setPosition([pos.coords.latitude, pos.coords.longitude]);
        },
        (err) => console.error(err),
        { enableHighAccuracy: true }
      );
    }
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
              <li>Latitude: {position[0]}</li>
              <li>Longitude: {position[1]}</li>
              <li>Última atualização: {new Date().toLocaleTimeString()}</li>
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
