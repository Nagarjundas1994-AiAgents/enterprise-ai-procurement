// CAP CDS query globals injected at runtime (SELECT/INSERT/UPDATE/UPSERT/DELETE).
declare global {
  const SELECT: any;
  const INSERT: any;
  const UPDATE: any;
  const UPSERT: any;
  const DELETE: any;
}
export {};
