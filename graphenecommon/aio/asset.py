# -*- coding: utf-8 -*-
from asyncinit import asyncinit
from ..exceptions import AssetDoesNotExistsException
from ..asset import Asset as SyncAsset


@asyncinit
class Asset(SyncAsset):
    async def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.asset_data_class

        self.full = kwargs.pop("full", False)
        self.__data = {}

        # Try load from cache
        data = self.asset_data_class(*args, **kwargs)
        if data:
            self.__data = data
        else:
            # Load from chain
            self.identifier = args[0]
            await self.refresh()

    async def refresh(self):
        """ Refresh the data from the API server
        """
        asset = await self.blockchain.rpc.get_asset(self.identifier)
        if not asset:
            raise AssetDoesNotExistsException(self.identifier)
        self.__data = self.asset_data_class(asset)
        if self.full:
            if "bitasset_data_id" in asset:
                self["bitasset_data"] = await self.blockchain.rpc.get_object(
                    asset["bitasset_data_id"]
                )
            self["dynamic_asset_data"] = await self.blockchain.rpc.get_object(
                asset["dynamic_asset_data_id"]
            )

    async def update_cer(self, cer, account=None, **kwargs):
        """ Update the Core Exchange Rate (CER) of an asset
        """
        assert callable(self.blockchain.update_cer)
        return await self.blockchain.update_cer(
            self["symbol"], cer, account=account, **kwargs
        )
