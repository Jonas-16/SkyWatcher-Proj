import { useEffect, useState } from "react";
import api from "@/api/api";
import { Plus, MapPin, Calendar, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";

interface Trip {
  id: string | number;
  name: string;
  location: string;
  startDate?: string;
  endDate?: string;
  start_date?: string;
  end_date?: string;
  weatherScore?: number;
  conditions?: string[];
  conditions_checklist?: string[];
}


const Trips = () => {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [newTrip, setNewTrip] = useState({
    name: "",
    location: "",
    startDate: "",
    endDate: "",
  });
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch trips on mount and fetch weather scores for each
  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getTrips()
      .then(async (tripsData) => {
        // For each trip, fetch weather score
        const tripsWithWeather = await Promise.all(
          (tripsData || []).map(async (trip: any) => {
            const start = trip.startDate || trip.start_date;
            const end = trip.endDate || trip.end_date;
            let weatherScore = null;
            try {
              const weather = await api.getWeatherProbability({
                location: trip.location,
                start_date: start?.split("T")[0],
                end_date: end?.split("T")[0],
                conditions_checklist: trip.conditions_checklist || [],
                activity_profile: trip.activity_type || ""
              });
              weatherScore = weather?.probabilities?.sunny ?? null;
            } catch {
              weatherScore = null;
            }
            return { ...trip, weatherScore };
          })
        );
        if (isMounted) setTrips(tripsWithWeather);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
    return () => { isMounted = false; };
  }, []);

  const handleCreateTrip = async () => {
    if (newTrip.name && newTrip.location && newTrip.startDate && newTrip.endDate) {
      setLoading(true);
      setError(null);
      try {
        const created = await api.createTrip(newTrip);
        // Fetch weather score for new trip
        let weatherScore = null;
        try {
          const weather = await api.getWeatherProbability({
            location: created.location,
            start_date: (created.startDate || created.start_date)?.split("T")[0],
            end_date: (created.endDate || created.end_date)?.split("T")[0],
            conditions_checklist: created.conditions_checklist || [],
            activity_profile: created.activity_type || ""
          });
          weatherScore = weather?.probabilities?.sunny ?? null;
        } catch {
          weatherScore = null;
        }
        setTrips((prev) => [...prev, { ...created, weatherScore }]);
        setNewTrip({ name: "", location: "", startDate: "", endDate: "" });
        setIsOpen(false);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleDeleteTrip = async (id: string | number) => {
    setLoading(true);
    setError(null);
    try {
      await api.deleteTrip(id);
      setTrips((prev) => prev.filter((trip) => trip.id !== id));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Trip Boards</h1>
          <p className="text-muted-foreground">
            Plan and track weather conditions for your upcoming trips
          </p>
        </div>

        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Trip
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Trip</DialogTitle>
              <DialogDescription>
                Add details for your trip to track weather conditions
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Trip Name</Label>
                <Input
                  id="name"
                  placeholder="Summer Vacation"
                  value={newTrip.name}
                  onChange={(e) => setNewTrip({ ...newTrip, name: e.target.value })}
                  disabled={loading}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  placeholder="Miami, FL"
                  value={newTrip.location}
                  onChange={(e) => setNewTrip({ ...newTrip, location: e.target.value })}
                  disabled={loading}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start">Start Date</Label>
                  <Input
                    id="start"
                    type="date"
                    value={newTrip.startDate}
                    onChange={(e) => setNewTrip({ ...newTrip, startDate: e.target.value })}
                    disabled={loading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end">End Date</Label>
                  <Input
                    id="end"
                    type="date"
                    value={newTrip.endDate}
                    onChange={(e) => setNewTrip({ ...newTrip, endDate: e.target.value })}
                    disabled={loading}
                  />
                </div>
              </div>
              {error && <div className="text-red-500 text-sm">{error}</div>}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsOpen(false)} disabled={loading}>
                Cancel
              </Button>
              <Button onClick={handleCreateTrip} disabled={loading}>
                {loading ? "Creating..." : "Create Trip"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {loading && <div>Loading...</div>}
      {error && <div className="text-red-500">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {(Array.isArray(trips) ? trips : []).map((trip) => {
          if (!trip) return null;
          const start = trip.startDate || trip.start_date;
          const end = trip.endDate || trip.end_date;
          const weatherScore = typeof trip.weatherScore === 'number' ? trip.weatherScore : null;
          const conditions = trip.conditions ?? trip.conditions_checklist ?? [];
          return (
            <Card key={trip.id} className="p-6 space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-semibold mb-1">{trip.name}</h3>
                  <div className="flex items-center gap-2 text-muted-foreground text-sm">
                    <MapPin className="h-4 w-4" />
                    {trip.location}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDeleteTrip(trip.id)}
                  disabled={loading}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex items-center gap-2 text-sm">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span>
                  {start ? new Date(start).toLocaleDateString() : "-"} - {end ? new Date(end).toLocaleDateString() : "-"}
                </span>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Weather Score</span>
                  <span className="text-2xl font-bold text-primary">
                    {weatherScore !== null ? `${weatherScore}%` : <span className="text-xs text-muted-foreground">N/A</span>}
                  </span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-sky-gradient"
                    style={{ width: weatherScore !== null ? `${weatherScore}%` : '0%' }}
                  />
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {Array.isArray(conditions) && conditions.length > 0
                  ? conditions.map((condition, idx) => (
                      <Badge key={idx} variant="secondary">
                        {condition}
                      </Badge>
                    ))
                  : <span className="text-muted-foreground text-xs">No conditions</span>}
              </div>

              <Button variant="outline" className="w-full">
                View Details
              </Button>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default Trips;
