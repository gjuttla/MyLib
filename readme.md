# MyLib
Example .NET Framework project with `TargetFrameworkFallbackSearchPaths`. Reference assemblies are downloaded from NuGet with [a Python script](./referenceAssembliesDownloader.py) running [before certain MSBuild targets](./Directory.Build.targets).

## Build Requirements
* Visual Studio 2022  
* Python 3  
    * module `requests` (`pip install requests`) 

## Build

Build with a clean repo / `git clean -xfd`.

| Building via  | Result |
| ------------- | ------------- |
| `dotnet build` | :heavy_check_mark: |
| `msbuild -t:Restore MyLib.sln` \[1\] (restore only)  | :heavy_check_mark: |
| `msbuild /restore MyLib.csproj` \[1\] | :heavy_check_mark: |
| VS 2022 (open solution and build project) | :x: |

\[1\] Using msbuild version included with VS 2022. 
