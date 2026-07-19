using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Backend.Events;

using System.Net.Http;
using System.Text;
using System.Text.Json;

using ETS2LA.Game;
using ETS2LA.Game.Data;
using ETS2LA.Game.SiiFiles;
using ETS2LA.Game.PpdFiles;
using ETS2LA.Game.Telemetry;
using TruckLib.ScsMap;

namespace DataCollection;

// Most of the logic here was copied from ETS2LA/official-plugins -> InternalVisualization
// Check that file for more information on how to use roads or prefabs, specifically these files:
// https://github.com/ETS2LA/official-plugins/blob/main/Plugins/InternalVisualization/Renderers/Roads.cs#L25-L134
// https://github.com/ETS2LA/official-plugins/blob/main/Plugins/InternalVisualization/Renderers/Prefabs.cs#L32-L177

public class DataCollection : Plugin
{
    public override PluginInformation Info => new PluginInformation
    {
        Id = "ets2la.datacollection",
        Version = "1.0.0",
        Name = "Data Collection",
        Description = "ETS2LA will collect driving data for possible future ML model training.",
        AuthorName = "Tumppi066", // Currently only one string, so add ', name' for multiple authors
        Dependencies = new List<string>{} // ETS2LA plugin dependencies, not NuGet dependencies.
    };

    public override float TickRate => 1f;
    private int ViewDistance = 300;

    private GameTelemetryData latestTelemetryData;
    private MapData? mapData;
    private Road[]? roads;
    private Prefab[]? prefabs;
    private IReadOnlyList<Node>? nearbyNodes;

    public override void Init()
    {
        base.Init();
        // This is run once when the plugin is initially loaded.
        // Usually you start to listen to control events here (or register your own).
        // ControlHandler.Current.On(ControlHandler.Defaults.Next.Id, OnNextPressed);
    }

    public override void OnEnable()
    {
        base.OnEnable();
        // Subscribe to events here, do not subscribe in Init as that's too early.
        // Events.Current.Subscribe<YourEventType>("YourTopic", YourEventHandler);

        Events.Current.Subscribe<GameTelemetryData>(GameTelemetry.Current.EventString, OnTelemetryUpdated);
    }

    private void OnTelemetryUpdated(GameTelemetryData data)
    {
        latestTelemetryData = data;
    }

    private void UpdateInstallation()
    {
        int installationIndex = 0;
        bool found = false;
        foreach (var item in GameHandler.Current.Installations)
        {
            if(item.IsParsed) {
                found = true; 
                break;
            }
            installationIndex++;
        }

        if (!found) return;
        MapData newData = GameHandler.Current.Installations[installationIndex].GetMapData();
        if (newData == mapData) return;
        mapData = newData;

        // If the data is found, we then update the file handlers and extract the latest roads and prefabs.
        // Note that this file handler step will be removed later, having it here won't break any new implementation
        // though.
        var fs = GameHandler.Current.Installations[installationIndex].GetFileSystem();
        if(fs != null) SiiFileHandler.Current.SetFileSystem(fs);
        if(fs != null) PpdFileHandler.Current.SetFileSystem(fs);

        roads = mapData.MapItems.Values.OfType<Road>().ToArray();
        prefabs = mapData.MapItems.Values.OfType<Prefab>().ToArray();

        // And we get the nearby nodes as well, this is used to find all roads/prefabs within the render distance.
        // Check the linked files up top for more information.
        // WARN: Some roads are up to 1024m long, in rare cases that means neither of their nodes are in render distance,
        //       and as such they will be determined as not nearby if you use the linked implementation.
        if (latestTelemetryData == null) return;
        Vector3Double center = latestTelemetryData.truckPlacement.coordinate;
        double minX = center.X - ViewDistance;
        double maxX = center.X + ViewDistance;
        double minZ = center.Z - ViewDistance;
        double maxZ = center.Z + ViewDistance;
        nearbyNodes = mapData.Nodes.Within(minX, minZ, maxX, maxZ);
    }

    public override void Tick()
    {
        UpdateInstallation();

        SendSnapshot(new Snapshot
        {
            Speed = 0,
            Steering = 0,
            Throttle = 0,
            Brake = 0
        }).Wait();
    }
    
    public async Task SendSnapshot(Snapshot payload)
    {
        using var client = new HttpClient();
        string json = JsonSerializer.Serialize(payload);
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        
        await client.PostAsync("https://ingest.ets2la.com/data.collection", content);
    }

    public override void OnDisable()
    {
        base.OnDisable();

        // Cleanup our references so they can be garbage collected.
        // When that happens is not critical.
        mapData = null;
        roads = null;
        prefabs = null;
        nearbyNodes = null;
    }

    public override void Shutdown()
    {
        base.Shutdown();
        // This is run once when the plugin is unloaded (at app shutdown), use it to clean up any resources or
        // threads you created in Init or elsewhere.
    }
}
