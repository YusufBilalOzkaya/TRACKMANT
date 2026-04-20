import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Plus, 
  RefreshCw, 
  ExternalLink, 
  Trash2, 
  Bell, 
  Activity,
  Globe,
  Mail,
  Settings,
  Pencil,
  X,
  Clock
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = "http://localhost:8000";

function App() {
  const [trackers, setTrackers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [editingTracker, setEditingTracker] = useState(null);
  
  const [settings, setSettings] = useState({ check_interval_minutes: 2 });
  const [newTracker, setNewTracker] = useState({
    name: '',
    url: '',
    selector: '',
    condition: 'changes',
    target_value: '',
    user_email: ''
  });

  const fetchTrackers = async () => {
    try {
      const res = await axios.get(`${API_BASE}/trackers`);
      setTrackers(res.data);
    } catch (err) {
      console.error("Failed to fetch trackers", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSettings = async () => {
    try {
      const res = await axios.get(`${API_BASE}/settings`);
      setSettings(res.data);
    } catch (err) {
      console.error("Failed to fetch settings", err);
    }
  };

  useEffect(() => {
    fetchTrackers();
    fetchSettings();
  }, []);

  const handleAddTracker = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/trackers`, {
        ...newTracker,
        target_value: newTracker.target_value ? parseFloat(newTracker.target_value) : null
      });
      setShowAddModal(false);
      fetchTrackers();
      setNewTracker({ name: '', url: '', selector: '', condition: 'changes', target_value: '', user_email: '' });
    } catch (err) {
      alert("Error adding tracker");
    }
  };

  const handleUpdateTracker = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${API_BASE}/trackers/${editingTracker.id}`, {
        ...editingTracker,
        target_value: editingTracker.target_value ? parseFloat(editingTracker.target_value) : null
      });
      setEditingTracker(null);
      fetchTrackers();
    } catch (err) {
      alert("Update failed");
    }
  };

  const updateSettings = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/settings`, settings);
      setShowSettingsModal(false);
      alert("Settings updated. Timer restarted.");
    } catch (err) {
      alert("Failed to save settings");
    }
  };

  const deleteTracker = async (id) => {
    if (!window.confirm("Are you sure you want to delete this tracker?")) return;
    try {
      await axios.delete(`${API_BASE}/trackers/${id}`);
      fetchTrackers();
    } catch (err) {
      alert("Delete failed");
    }
  };

  const manuallyCheck = async (id) => {
    try {
      await axios.post(`${API_BASE}/trackers/${id}/check`);
      fetchTrackers();
    } catch (err) {
      alert("Check failed");
    }
  };

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary p-8 font-sans">
      {/* Background Orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-accent-purple/20 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[400px] h-[400px] bg-accent-blue/15 blur-[100px] rounded-full" />
      </div>

      <header className="max-w-7xl mx-auto mb-12 flex justify-between items-center relative z-10">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-white to-accent-purple bg-clip-text text-transparent">
            TRACKMANT
          </h1>
          <p className="text-gray-500 mt-2 flex items-center gap-2">
            <Activity size={16} className="text-accent-green" /> 
            Universal Monitoring System Active | Every {settings.check_interval_minutes} min.
          </p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={() => setShowSettingsModal(true)}
            title="General Settings"
            className="p-3 glass glass-hover rounded-xl text-gray-400 transition-all"
          >
            <Settings size={20} />
          </button>
          <button 
            onClick={() => fetchTrackers()}
            className="p-3 glass glass-hover rounded-xl text-gray-400 transition-all hover:rotate-180"
          >
            <RefreshCw size={20} />
          </button>
          <button 
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 bg-accent-purple px-6 py-3 rounded-xl font-bold hover:brightness-110 transition-all shadow-lg shadow-accent-purple/20"
          >
            <Plus size={20} /> New Tracker
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto relative z-10">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-purple" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
            {trackers.map((tracker) => (
              <TrackerCard 
                key={tracker.id} 
                tracker={tracker} 
                onCheck={() => manuallyCheck(tracker.id)} 
                onDelete={() => deleteTracker(tracker.id)}
                onEdit={() => setEditingTracker(tracker)}
              />
            ))}
            {trackers.length === 0 && (
              <div className="col-span-full py-20 text-center glass rounded-3xl">
                <Globe size={48} className="mx-auto text-gray-700 mb-4" />
                <p className="text-gray-500">No trackers created yet.</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Settings Modal */}
      <Modal show={showSettingsModal} onClose={() => setShowSettingsModal(false)} title="System Settings">
        <form onSubmit={updateSettings} className="space-y-6">
          <div className="bg-white/5 p-4 rounded-2xl border border-white/5">
             <div className="flex items-center gap-4 mb-4">
                <div className="bg-accent-blue/20 p-3 rounded-xl">
                    <Clock className="text-accent-blue" size={24} />
                </div>
                <div>
                    <h3 className="font-bold">Auto-Check Timer</h3>
                    <p className="text-xs text-gray-500">How often should the system check all trackers?</p>
                </div>
             </div>
             <div className="flex items-center gap-4">
                <input 
                  type="number" 
                  min="1"
                  className="flex-1 bg-black/20 border border-white/10 rounded-xl p-3 outline-none focus:border-accent-blue"
                  value={settings.check_interval_minutes}
                  onChange={e => setSettings({...settings, check_interval_minutes: parseInt(e.target.value) || 1})}
                />
                <span className="font-bold text-gray-400">Minutes</span>
             </div>
          </div>
          <button type="submit" className="w-full bg-accent-blue py-4 rounded-xl font-bold shadow-lg shadow-accent-blue/20 hover:brightness-110">
            Update Timer
          </button>
        </form>
      </Modal>

      <Modal 
        show={showAddModal || !!editingTracker} 
        onClose={() => {setShowAddModal(false); setEditingTracker(null);}} 
        title={editingTracker ? "Edit Tracker" : "Add New Tracker"}
      >
        <form onSubmit={editingTracker ? handleUpdateTracker : handleAddTracker} className="space-y-6">
          <input 
            required
            className="w-full bg-white/5 border border-white/10 rounded-xl p-3 outline-none focus:border-accent-purple"
            placeholder="Tracker Name (e.g. Graphics Card)"
            value={editingTracker ? editingTracker.name : newTracker.name}
            onChange={e => editingTracker ? setEditingTracker({...editingTracker, name: e.target.value}) : setNewTracker({...newTracker, name: e.target.value})}
          />
          <input 
            required
            type="url"
            className="w-full bg-white/5 border border-white/10 rounded-xl p-3 outline-none focus:border-accent-purple"
            placeholder="URL (https://...)"
            value={editingTracker ? editingTracker.url : newTracker.url}
            onChange={e => editingTracker ? setEditingTracker({...editingTracker, url: e.target.value}) : setNewTracker({...newTracker, url: e.target.value})}
          />
          <input 
            required
            className="w-full bg-white/5 border border-white/10 rounded-xl p-3 outline-none focus:border-accent-purple font-mono text-sm"
            placeholder="CSS Selector"
            value={editingTracker ? editingTracker.selector : newTracker.selector}
            onChange={e => editingTracker ? setEditingTracker({...editingTracker, selector: e.target.value}) : setNewTracker({...newTracker, selector: e.target.value})}
          />
          <div className="flex gap-4">
            <select 
              className="flex-1 bg-white/5 border border-white/10 rounded-xl p-3 outline-none focus:border-accent-purple"
              value={editingTracker ? editingTracker.condition : newTracker.condition}
              onChange={e => editingTracker ? setEditingTracker({...editingTracker, condition: e.target.value}) : setNewTracker({...newTracker, condition: e.target.value})}
            >
              <option value="changes">When Price Changes</option>
              <option value="below">When Below Target</option>
              <option value="above">When Above Target</option>
            </select>
            {(editingTracker?.condition !== 'changes' && newTracker.condition !== 'changes') && (
               <input 
                 type="number"
                 step="any"
                 className="flex-1 bg-white/5 border border-white/10 rounded-xl p-3 outline-none focus:border-accent-purple"
                 placeholder="Target Value"
                 value={editingTracker ? editingTracker.target_value : newTracker.target_value}
                 onChange={e => editingTracker ? setEditingTracker({...editingTracker, target_value: e.target.value}) : setNewTracker({...newTracker, target_value: e.target.value})}
               />
            )}
          </div>
          <input 
            required
            type="email"
            className="w-full bg-white/5 border border-white/10 rounded-xl p-3 outline-none focus:border-accent-purple"
            placeholder="Notification Email"
            value={editingTracker ? editingTracker.user_email : newTracker.user_email}
            onChange={e => editingTracker ? setEditingTracker({...editingTracker, user_email: e.target.value}) : setNewTracker({...newTracker, user_email: e.target.value})}
          />
          <button type="submit" className="w-full bg-accent-purple py-4 rounded-xl font-bold mt-4 hover:brightness-110">
            {editingTracker ? "Save Changes" : "Start Tracking"}
          </button>
        </form>
      </Modal>
    </div>
  );
}

function Modal({ show, onClose, title, children }) {
  return (
    <AnimatePresence>
      {show && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
            className="relative w-full max-w-lg glass p-10 rounded-[32px] border-white/10 shadow-2xl"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">{title}</h2>
              <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-all">
                <X size={20} />
              </button>
            </div>
            {children}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

function TrackerCard({ tracker, onCheck, onDelete, onEdit }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      layout
      className="glass p-8 rounded-[32px] relative group overflow-hidden border border-white/5"
    >
      <div className="flex justify-between items-start mb-8">
        <div className="bg-white/5 p-4 rounded-2xl group-hover:bg-accent-purple/20 transition-all">
          <Globe className="text-gray-500 group-hover:text-accent-purple" size={24} />
        </div>
        <div className="flex gap-3 opacity-0 group-hover:opacity-100 transition-all translate-y-2 group-hover:translate-y-0">
          <button onClick={onEdit} title="Edit" className="p-2.5 bg-white/5 hover:bg-accent-blue/20 rounded-xl text-gray-400 hover:text-accent-blue transition-all">
            <Pencil size={18} />
          </button>
          <button onClick={onCheck} title="Check Now" className="p-2.5 bg-white/5 hover:bg-white/10 rounded-xl text-gray-400 hover:text-white transition-all">
            <RefreshCw size={18} />
          </button>
          <button onClick={onDelete} title="Delete Tracker" className="p-2.5 bg-white/5 hover:bg-red-500/20 rounded-xl text-gray-400 hover:text-red-400 transition-all">
            <Trash2 size={18} />
          </button>
        </div>
      </div>

      <h3 className="text-2xl font-bold mb-2 truncate text-white/90">{tracker.name}</h3>
      <div className="flex items-center gap-2 mb-8">
          <p className="text-sm text-gray-500 truncate max-w-[150px] font-medium">{new URL(tracker.url).hostname}</p>
          <a href={tracker.url} target="_blank" rel="noreferrer" className="text-accent-purple/60 hover:text-accent-purple transition-colors"><ExternalLink size={14} /></a>
      </div>

      <div className="flex items-end justify-between mb-8">
        <div>
          <span className="block text-[10px] uppercase tracking-[0.2em] text-gray-500 font-black mb-2">Current Value</span>
          <div className="text-4xl font-black text-accent-green leading-none">
            {tracker.last_value || <span className="text-gray-700">Waiting...</span>}
          </div>
        </div>
        <div className="pb-1">
          <div className={`flex items-center gap-1.5 text-xs font-bold px-4 py-1.5 rounded-full ${tracker.last_value ? 'text-accent-blue bg-accent-blue/10 border border-accent-blue/20' : 'text-gray-500 bg-white/5 animate-pulse border border-white/5'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${tracker.last_value ? 'bg-accent-blue animate-pulse' : 'bg-gray-700'}`} />
            {tracker.last_value ? 'Active' : 'Standby'}
          </div>
        </div>
      </div>

      <div className="mt-8 pt-8 border-t border-white/5 flex justify-between items-center text-xs text-gray-500">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-accent-purple/10 flex items-center justify-center">
            <Bell size={12} className="text-accent-purple" /> 
          </div>
          <span className="capitalize font-semibold">{tracker.condition}</span>
        </div>
        <div className="flex items-center gap-2 bg-white/5 px-3 py-1.5 rounded-xl">
          <Mail size={12} /> {tracker.user_email}
        </div>
      </div>
    </motion.div>
  );
}

export default App;
