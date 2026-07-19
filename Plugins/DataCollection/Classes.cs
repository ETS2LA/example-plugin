using System;
namespace DataCollection;

// All variables going into this class have to be [Serializable]
// So if you intend on sending map data, you'll likely want to create a new class
// with an initializer from ParsedRoad, ParsedPrefab, etc...

[Serializable]
public class Snapshot
{
    public float Speed { get; set; }
    public float Steering { get; set; }
    public float Throttle { get; set; }
    public float Brake { get; set; }
}